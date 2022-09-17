from __future__ import annotations

import copy
import numpy as np
from typing import Dict, List

from networkx import has_path, connected_components
from z3 import Bool

from core.Crossbar import Crossbar
from aux.DotGenerator import DotGenerator
from aux.LatexGenerator import LatexGenerator
from core.Literal import Literal


class MemristorCrossbar(Crossbar):
    """
    Type of crossbar where literals are assigned to memristors.
    """

    def __init__(self, rows: int, columns: int, layers: int = 1, default_literal=Literal("False", False)):
        """
        Constructs a memristor crossbar of dimensions (number of memristors) x by y.
        The optional dimension layers indicates the number of layers of memristors.
        By default, the number of layers is 1.
        A memristor is defined by a triple (l, r, c) where r is the index of the nanowire below the memristor,
        c is the index of the nanowire above the memristor, and l is the layer of the memristor.
        A nanowire is defined by a tuple (l, i) where i is the index in a series of parallel nanowires at layer l.
        :param rows: The number of memristors along the input and output nanowires.
        :param columns: The number of memristors orthogonal to the input and output nanowires.
        :param layers: The number of layers of memristors.
        """
        super(MemristorCrossbar, self).__init__(rows, columns, layers, default_literal)
        self.input_rows = None

    def merge(self) -> Crossbar:
        # TODO: Implement
        pass

    def __copy__(self):
        crossbar = MemristorCrossbar(self.rows, self.columns, self.layers)
        crossbar.matrix = copy.deepcopy(self.matrix)
        # for layer in range(self.layers):
        #     for r in range(self.rows):
        #         for c in range(self.columns):
        #             memristor = self.get_memristor(r, c)
        #             stuck_at_fault = memristor.stuck_at_fault
        #             permanent = memristor.permanent
        #             crossbar.set_memristor(r, c, self.get_memristor(r, c).literal, layer, stuck_at_fault=stuck_at_fault,
        #                                    permanent=permanent)
        crossbar.input_nanowires = self.input_nanowires
        crossbar.input_variables = self.input_variables.copy()
        crossbar.output_nanowires = self.output_nanowires.copy()
        return crossbar

    # def __eq__(self, other):
    #     if not isinstance(other, MemristorCrossbar):
    #         return False
    #     dgt = DynamicGraphTree(other)
    #     benchmark = Benchmark('', self.input_variables, self.output_variables, self.z3())
    #     return dgt.is_equivalent(benchmark)

    def get_graph(self):
        return self.graph()

    def get_matrix(self):
        return self.matrix

    def find_equivalent_components(self) -> List:
        graph = self.graph()
        o_non_one_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                           not (d['atom'] == 'True' and d['positive'])]
        graph.remove_edges_from(o_non_one_edges)

        equivalent = [list(f) for f in connected_components(graph)]
        return equivalent

    @staticmethod
    def _find_equivalent_row_or_column(equivalent: List, layer: int):
        """
        The axis 0 denotes one axis, and the axis 1 denotes the perpendicular axis of nanowires.
        :param equivalent:
        :param axis:
        :return:
        """
        f = [list(map(lambda w: int(w[3:]), filter(lambda x: x[1] == str(layer), equivalent_subset))) for equivalent_subset in equivalent]
        return f

    def get_equivalent_rows(self) -> List:
        equivalent = self.find_equivalent_components()
        return self._find_equivalent_row_or_column(equivalent, 0)

    def get_equivalent_columns(self) -> List:
        equivalent = self.find_equivalent_components()
        return self._find_equivalent_row_or_column(equivalent, 1)

    def get_lits(self):
        literals = set()
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal != Literal('True', True) and self.get_memristor(r, c).literal != Literal('False',
                                                                                                               False):
                    literals.add(self.get_memristor(r, c).literal)
        return literals

    def get_vars(self):
        variables = set()
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal != Literal('True', True) and self.get_memristor(r, c).literal != Literal('False',
                                                                                                               False):
                    variables.add(self.get_memristor(r, c).literal.atom)
        return variables

    def get_nr_variables(self):
        count = 0
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal != Literal('True', True) and self.get_memristor(r, c).literal != Literal('False',
                                                                                                               False):
                    count += 1
        return count

    def get_ternary_matrix(self, layer: int = 0) -> np.ndarray:
        """
        TODO: Adapt to handle all layers, currently only handles one layer (layer 0)
        :param layer:
        :return:
        """
        ternary_matrix = np.empty((self.rows, self.columns))
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal == Literal("True", True):
                    ternary_matrix[r, c] = 1
                elif self.get_memristor(r, c).literal == Literal("False", False):
                    ternary_matrix[r, c] = -1
                else:
                    ternary_matrix[r, c] = 0
        return ternary_matrix

    def compress(self) -> MemristorCrossbar:
        ternary_matrix = self.get_ternary_matrix()
        equivalent_rows = self.get_equivalent_rows()
        compressed_rows = self._compress_equivalent_rows(ternary_matrix, equivalent_rows)
        row_compressed_crossbar = MemristorCrossbar.nd_array_to_crossbar(compressed_rows)
        equivalent_columns = row_compressed_crossbar.get_equivalent_columns()
        compressed_columns = self._compress_equivalent_columns(compressed_rows, equivalent_columns)
        compressed_crossbar = MemristorCrossbar.nd_array_to_crossbar(compressed_columns)
        # print(compressed_crossbar.rows)
        # print(compressed_crossbar.columns)
        return compressed_crossbar

    @staticmethod
    def nd_array_to_crossbar(nd_array: np.ndarray) -> MemristorCrossbar:
        crossbar = MemristorCrossbar(nd_array.shape[0], nd_array.shape[1])
        for r in range(nd_array.shape[0]):
            for c in range(nd_array.shape[1]):
                if nd_array[r, c] == 1:
                    crossbar.set_memristor(r, c, Literal("True", True))
                elif nd_array[r, c] == -1:
                    crossbar.set_memristor(r, c, Literal("False", False))
                else:
                    crossbar.set_memristor(r, c, Literal("x", True))
        return crossbar

    @staticmethod
    def _compress_equivalent_rows(ternary_matrix: np.ndarray, equivalent_rows: List) -> np.ndarray:
        rows = []
        for group in equivalent_rows:
            if len(group) > 0:
                a = np.amax(np.array(list(map(lambda x: ternary_matrix[x, :], group))), axis=0)
                rows.append([a])
        if rows:
            n = np.concatenate(rows)
        else:
            n = ternary_matrix
        return n

    @staticmethod
    def _compress_equivalent_columns(ternary_matrix, equivalent_columns: List) -> np.ndarray:
        cols = []
        for group in equivalent_columns:
            if len(group) > 0:
                a = np.amax(np.array(list(map(lambda x: ternary_matrix[:, x], group))), axis=0)
                cols.append([a])
        if cols:
            n = np.concatenate(cols).transpose()
        else:
            n = ternary_matrix
        return n

    def transpose(self) -> MemristorCrossbar:
        crossbar = MemristorCrossbar(self.columns, self.rows)
        for r in range(self.rows):
            for c in range(self.columns):
                crossbar.set_memristor(c, r, self.get_memristor(r, c).literal)
        crossbar.input_variables = self.input_variables.copy()
        crossbar.output_nanowires = self.output_nanowires.copy()
        return crossbar

    def get_z3(self) -> Dict[str, Bool]:
        # dgt = DynamicGraphTree(self)
        # formulae = dict()
        # for output_variable in self.output_variables.keys():
        #     formulae[output_variable] = dgt.to_formula(output_variable)
        # return formulae
        return dict()

    def instantiate(self, instance: dict) -> MemristorCrossbar:
        for layer in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    memristor = self.get_memristor(r, c, layer)
                    literal = memristor.literal
                    variable_name = literal.atom
                    positive = literal.positive
                    if variable_name != "True" and variable_name != "False":
                        if not memristor.stuck_at_fault:
                            if positive:
                                if instance[variable_name]:
                                    literal = Literal('True', True)
                                else:
                                    literal = Literal('False', False)
                            else:
                                if instance[variable_name]:
                                    literal = Literal('False', False)
                                else:
                                    literal = Literal('True', True)
                            self.set_memristor(r, c, literal, layer=layer)
        return self

    def write_xbar(self) -> str:
        content = ""
        # content += ".model {}\n".format(self.name)
        content += ".inputs {}\n".format(' '.join(self.get_input_variables()))
        content += ".outputs {}\n".format(' '.join(self.get_output_variables()))
        content += ".rows {}\n".format(self.rows)
        content += ".columns {}\n".format(self.columns)
        for (input_variable, (layer, nanowire)) in self.get_input_nanowires().items():
            content += ".i {} {} {}\n".format(input_variable, layer, nanowire)
        for (output_variables, (layer, nanowire)) in self.get_output_nanowires().items():
            if isinstance(output_variables, str):
                content += ".o {} {} {}\n".format(output_variables, layer, nanowire)
            else:
                content += ".o {} {} {}\n".format(" ".join(output_variables), layer, nanowire)
        content += ".xbar\n"
        for r in range(self.rows):
            for c in range(self.columns):
                literal = str(self.get_memristor(r, c).literal)
                if c < self.columns - 1:
                    content += "{}\t".format(literal)
                else:
                    content += "{}\n".format(literal)
        content += ".end\n"
        return content

    def eval(self, instance: Dict[str, bool], input_function: str = "1") -> Dict[str, bool]:
        # For all input nanowires different from a different input function than the given input function,
        # we set the literals False to avoid any loops through these nanowires.
        for (other_input_function, (layer, input_nanowire)) in self.get_input_nanowires().items():
            if input_function != other_input_function:
                for c in range(self.columns):
                    self.set_memristor(input_nanowire, c, Literal("False", False), layer=layer)

        crossbar_copy = self.__copy__()
        crossbar_instance = crossbar_copy.instantiate(instance)
        graph = crossbar_instance.graph()
        true_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                              not (d['atom'] == 'True' and d['positive'])]
        graph.remove_edges_from(true_edges)

        evaluation = dict()
        for (output_variable, (output_layer, output_nanowire)) in crossbar_instance.get_output_nanowires().items():
            source = "L{}_{}".format(output_layer, output_nanowire)
            input_layer, input_nanowire = crossbar_instance.get_input_nanowire(input_function)
            sink = "L{}_{}".format(input_layer, input_nanowire)
            evaluation[output_variable] = has_path(graph, source, sink)

        return evaluation

    def draw_graph(self, benchmark_name: str):
        content = ''
        content += 'graph{\n'

        graph = self.graph()
        false_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                       d['atom'] == 'False' and not d['positive']]
        graph.remove_edges_from(false_edges)

        for v in graph.nodes:
            node_attributes = v[1:]
            (layer, index) = node_attributes.split("_")
            content += '{} [layer="{}"]\n'.format(v, layer)

        for (u, v, d) in graph.edges(data=True):
            if d["positive"]:
                if d["atom"] == "True":
                    literal = "1"
                else:
                    literal = d["atom"]
            else:
                literal = "~" + d["atom"]
            content += '{} -- {} [label="{}"]\n'.format(u, v, literal)

        content += '}\n'

        DotGenerator.generate(benchmark_name, content)

    # def draw_graph(self, benchmark_name: str):
    #     """
    #     TODO: Remove benchmark_name for future use.
    #     Draws a graph representation of this memristor crossbar in LateX for each layer of memristors in this
    #     memristor crossbar.
    #     :param benchmark_name: The given name for the benchmark.
    #     :return:
    #     """
    #     content = ''
    #     content += '\\documentclass{article}\n'
    #     content += '\\usepackage{tikz,amsmath,siunitx}\n'
    #     content += '\\usetikzlibrary{arrows,snakes,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks}\n'
    #     content += '\\usepackage[graphics,tightpage,active]{preview}\n'
    #     content += '\\PreviewEnvironment{tikzpicture}\n'
    #     content += '\\PreviewEnvironment{equation}\n'
    #     content += '\\PreviewEnvironment{equation*}\n'
    #     content += '\\newlength{\imagewidth}\n'
    #     content += '\\newlength{\imagescale}\n'
    #     content += '\\pagestyle{empty}\n'
    #     content += '\\thispagestyle{empty}\n'
    #     content += '\\begin{document}\n'
    #     content += '\\begin{tikzpicture}[OFF/.style={circle, draw, fill = gray!40, minimum size=8, inner sep=0pt, ' \
    #                'text width=6mm, align=center},BARE/.style={circle, draw=none, ' \
    #                'minimum size=8, inner sep=0pt, text width=6mm, align=center}, NODE/.style={circle, draw, ' \
    #                'minimum size=8, inner sep=0pt, text width=6mm, align=center}]\n'
    #
    #     graph = self.graph()
    #     false_edges = [(u, v) for u, v, d in graph.edges(data=True) if
    #                        d['atom'] == 'False' and not d['positive']]
    #     graph.remove_edges_from(false_edges)
    #
    #     if self.rows <= self.columns:
    #         smallest_dimension = 2
    #     else:
    #         smallest_dimension = 1
    #
    #     difference = (max(self.rows, self.columns) - min(self.rows, self.columns)) / 2
    #
    #     for node in graph.nodes:
    #         node_attributes = node[1:]
    #         (layer, index) = node_attributes.split("_")
    #         s = 'NODE'
    #         v = '$\\scriptscriptstyle L^{' + layer + '}_{' + index + '}$'
    #
    #         for (i, (l, r)) in self.input_nanowires.items():
    #             if int(layer) == l and r == int(index):
    #                 v = '$\\scriptscriptstyle L^{' + layer + '}_{' + index + '} = ' + i + '$'
    #         for (o, (l, r)) in self.output_variables.items():
    #             if int(layer) == l and r == int(index):
    #                 v = '$\\scriptscriptstyle L^{' + layer + '}_{' + index + '} = ' + o + '$'
    #
    #         if int(layer) % smallest_dimension == 0:
    #             content += '\\node[%s](n%d_%d) at (1.6*%d, 8*%d) {%s};\n' % (
    #                 s, int(index), self.rows - int(layer), int(index) + difference, self.rows - int(layer), v)
    #         else:
    #             content += '\\node[%s](n%d_%d) at (1.6*%d, 8*%d) {%s};\n' % (
    #                 s, int(index), self.rows - int(layer), int(index), self.rows - int(layer), v)
    #
    #     for (node_a, node_b, data) in graph.edges(data=True):
    #         node_attributes_a = node_a[1:]
    #         (layer_a, index_a) = node_attributes_a.split("_")
    #         node_attributes_b = node_b[1:]
    #         (layer_b, index_b) = node_attributes_b.split("_")
    #         if data["positive"]:
    #             if data["atom"] == "True":
    #                 content += '\\draw[green!40] (n%d_%d) -- (n%d_%d);\n' % (int(index_a), self.rows - int(layer_a), int(index_b), self.rows - int(layer_b))
    #             else:
    #                 literal = "$\\scriptscriptstyle " + data["atom"] + "$"
    #                 content += '\\draw (n%d_%d) -- (n%d_%d) node [near start, above=4pt, fill=white] {%s};\n' % (
    #                 int(index_a), self.rows - int(layer_a), int(index_b), self.rows - int(layer_b), str(literal))
    #         else:
    #             literal = "$\\scriptscriptstyle \\neg " + data["atom"] + "$"
    #             content += '\\draw (n%d_%d) -- (n%d_%d) node [near start, above=4pt, fill=white] {%s};\n' % (int(index_a), self.rows - int(layer_a), int(index_b), self.rows - int(layer_b), str(literal))
    #
    #
    #     # # We draw a separate crossbar matrix for each layer of memristors.
    #     # for layer in range(self.get_memristor_layers()):
    #     #     content += '\\textbf{Layer ' + str(layer) + '}\n'
    #     #     for c in range(self.columns):
    #     #         for r in range(self.rows):
    #     #             if self.get_memristor(r, c, layer).literal.atom == 'False':
    #     #                 v = '$\\scriptscriptstyle 0$'
    #     #                 s = 'OFF'
    #     #             elif self.get_memristor(r, c, layer).literal.atom == 'True':
    #     #                 v = '$\\scriptscriptstyle 1$'
    #     #                 s = 'ON'
    #     #             else:
    #     #                 if not self.get_memristor(r, c, layer).literal.positive:
    #     #                     v = '$\\scriptscriptstyle \\neg ' + self.get_memristor(r, c, layer).literal.atom + '$'
    #     #                 else:
    #     #                     v = '$\\scriptscriptstyle ' + self.get_memristor(r, c, layer).literal.atom + '$'
    #     #                 s = 'VAR'
    #     #             content += '\\node[%s](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
    #     #                 s, c + 1, self.rows - r, c + 1, self.rows - r, v)
    #     #
    #     #     for c in range(self.columns - 1):
    #     #         for r in range(self.rows):
    #     #             content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 2, r + 1)
    #     #
    #     #     for c in range(self.columns):
    #     #         for r in range(self.rows - 1):
    #     #             content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 1, r + 2)
    #     #
    #     #     # # Inputs
    #     #     for (i, r) in self.input_nanowires.items():
    #     #         v = '$\\scriptscriptstyle Vin_{}$'.format(i)
    #     #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
    #     #         0, self.rows - r, 0, self.rows - r, v)
    #     #         content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, self.rows - r, 1, self.rows - r)
    #
    #         # # Outputs
    #         # for (o, r) in self.output_variables.items():
    #         #     v = '$\\scriptscriptstyle ' + o + '$'
    #         #     content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
    #         #         self.columns + 1, self.rows - r, self.columns + 1, self.rows - r, v)
    #         #     content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (
    #         #     self.columns, self.rows - r, self.columns + 1, self.rows - r)
    #         #
    #         # # New page for each layer
    #         # if layer < self.get_memristor_layers() - 1:
    #         #     content += '\\newpage\n'
    #
    #     content += '\\end{tikzpicture}\n'
    #     content += '\\end{document}\n'
    #
    #     LatexGenerator.generate(benchmark_name, content)

    def draw_matrix(self, benchmark_name: str, draw_latex: bool = False):
        # TODO: Soon remove all Latex and replace with Graphviz' DOT
        if draw_latex:
            self.draw_latex_matrix(benchmark_name)
        else:
            self.draw_dot_matrix(benchmark_name)

    def draw_latex_matrix(self, benchmark_name: str):
        """
        TODO: Remove benchmark_name for future use.
        Draws a matrix representation of this memristor crossbar in LateX for each layer of memristors in this
        memristor crossbar.
        :param benchmark_name: The given name for the benchmark.
        :param draw_latex:
        :return:
        """
        # We draw a separate crossbar matrix for each layer of memristors.
        for layer in range(self.get_memristor_layers()):
            content = ''
            content += '\\documentclass{article}\n'
            content += '\\usepackage{tikz,amsmath,siunitx}\n'
            content += '\\usetikzlibrary{arrows,snakes,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks}\n'
            content += '\\usepackage[graphics,tightpage,active]{preview}\n'
            content += '\\PreviewEnvironment{tikzpicture}\n'
            content += '\\PreviewEnvironment{equation}\n'
            content += '\\PreviewEnvironment{equation*}\n'
            content += '\\newlength{\imagewidth}\n'
            content += '\\newlength{\imagescale}\n'
            content += '\\pagestyle{empty}\n'
            content += '\\thispagestyle{empty}\n'
            content += '\\begin{document}\n'
            content += '\\begin{tikzpicture}[STUCK/.style={circle, draw, fill = red!40, minimum size=8, inner sep=0pt, ' \
                       'text width=6mm, align=center},OFF/.style={circle, draw, fill = gray!40, minimum size=8, inner sep=0pt, ' \
                       'text width=6mm, align=center},ON/.style={circle, draw, fill = green!40, minimum size=8, ' \
                       'inner sep=0pt, text width=6mm, align=center},VAR/.style={circle, draw, fill = blue!40, ' \
                       'minimum size=8, inner sep=0pt, text width=6mm, align=center},BARE/.style={circle, draw=none, ' \
                       'minimum size=8, inner sep=0pt, text width=6mm, align=center}]\n'

            content += '\\textbf{Layer ' + str(layer) + '}\n'
            for c in range(self.columns):
                for r in range(self.rows):
                    if self.get_memristor(r, c, layer).literal.atom == 'False':
                        v = '$\\scriptscriptstyle 0$'
                        s = 'OFF'
                    elif self.get_memristor(r, c, layer).literal.atom == 'True':
                        v = '$\\scriptscriptstyle 1$'
                        s = 'ON'
                    else:
                        if not self.get_memristor(r, c, layer).literal.positive:
                            v = '$\\scriptscriptstyle \\neg ' + self.get_memristor(r, c, layer).literal.atom + '$'
                        else:
                            v = '$\\scriptscriptstyle ' + self.get_memristor(r, c, layer).literal.atom + '$'
                        s = 'VAR'
                    if self.get_memristor(r, c, layer).stuck_at_fault:
                        s = 'STUCK'
                    content += '\\node[%s](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
                        s, c + 1, self.rows - r, c + 1, self.rows - r, v)

            for c in range(self.columns - 1):
                for r in range(self.rows):
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 2, r + 1)

            for c in range(self.columns):
                for r in range(self.rows - 1):
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (c + 1, r + 1, c + 1, r + 2)

            # if self.layers == 1:
            #
            #     # Inputs
            #     for (i, r) in self.input_nanowires.items():
            #         v = '$\\scriptscriptstyle Vin_{}$'.format(i)
            #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (0, self.rows - r, 0, self.rows - r, v)
            #         content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, self.rows - r, 1, self.rows - r)
            #
            #     # # Outputs
            #     for (o, r) in self.output_variables.items():
            #         v = '$\\scriptscriptstyle ' + o + '$'
            #         content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
            #             self.columns + 1, self.rows - r, self.columns + 1, self.rows - r, v)
            #         content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (self.columns, self.rows - r, self.columns + 1, self.rows - r)
            # else:
            # TODO: Uncomment for 3D
            # Inputs
            for (i, (l, r)) in self.get_input_nanowires().items():
                if layer == l:
                    v = '$\\scriptscriptstyle Vin_{}$'.format(i)
                    content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (0, self.rows - r, 0, self.rows - r, v)
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (0, self.rows - r, 1, self.rows - r)

            # Outputs
            output_variables = dict()
            for (o, (l, r)) in self.output_nanowires.items():
                if (l, r) in output_variables:
                    output_variables[(l, r)].append(o)
                else:
                    output_variables[(l, r)] = [o]
            for ((l, r), os) in output_variables.items():
                if layer == l:
                    for i in range(len(os)):
                        o = os[i]
                        v = '$\\scriptscriptstyle ' + o + '$'
                        content += '\\node[BARE](n%d_%d) at (0.8*%d, 0.8*%d) {%s};\n' % (
                            self.columns + 1 + i, self.rows - r, self.columns + 1 + i, self.rows - r, v)
                    content += '\\draw (n%d_%d) -- (n%d_%d);\n' % (self.columns, self.rows - r, self.columns + 1, self.rows - r)

            content += '\\end{tikzpicture}\n'
            content += '\\end{document}\n'

            LatexGenerator.generate(benchmark_name + "_" + str(layer), content)

    def draw_dot_matrix(self, benchmark_name: str):
        # We draw a separate crossbar matrix for each layer of memristors.
        # Grid after https://graphviz.org/Gallery/undirected/grid.html
        # Node distance after https://newbedev.com/how-to-manage-distance-between-nodes-in-graphviz
        layer_contents = []
        layer_to_input_nanowires = dict()
        for i, (l, r) in self.input_nanowires.items():
            if l not in layer_to_input_nanowires:
                layer_to_input_nanowires[l] = []
            else:
                layer_to_input_nanowires[l].append(i)

        layer_to_output_nanowires = dict()
        for o, (l, r) in self.output_nanowires.items():
            if l not in layer_to_input_nanowires:
                layer_to_output_nanowires[l] = []
            else:
                layer_to_output_nanowires[l].append(o)

        for layer in range(self.get_memristor_layers()):
            layer_content = ''
            layer_content += 'graph {} {{\n'.format(benchmark_name)
            layer_content += '\tgraph [nodesep="0.2", ranksep="0.2"];\n'
            layer_content += '\tcharset="UTF-8";\n'
            layer_content += '\tratio=fill;\n'
            layer_content += '\tsplines=polyline;\n'
            layer_content += '\toverlap=scale;\n'
            layer_content += '\tnode [shape=circle, fixedsize=true, width=0.4, fontsize=8];\n'
            layer_content += '\n'

            layer_content += '\n\t// Memristors\n'
            for c in range(self.columns):
                for r in range(self.rows):
                    if self.get_memristor(r, c, layer).literal.atom == 'False':
                        v = '0'
                        style = 'color="#000000", fillcolor="#eeeeee", style="filled,solid"'
                    elif self.get_memristor(r, c, layer).literal.atom == 'True':
                        v = '1'
                        style = 'color="#000000", fillcolor="#cadfb8", style="filled,solid"'
                    else:
                        if not self.get_memristor(r, c, layer).literal.positive:
                            v = '¬' + self.get_memristor(r, c, layer).literal.atom
                        else:
                            v = self.get_memristor(r, c, layer).literal.atom
                        style = 'color="#000000", fillcolor="#b4c7e7", style="filled,solid"'
                    layer_content += '\tm{}_{} [label="{}" {}]\n'.format(r + 1, c + 1, v, style)

            layer_content += '\n\t// Functions (left y-axis)\n'
            # Functions
            for r in range(self.rows):
                input_rows = list(map(lambda i: i[1], self.get_input_nanowires().values()))
                style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
                if r not in input_rows:
                    v = ''  # '{}'.format(self.functions[r][0])
                    layer_content += '\tm{}_{} [label="{}" {}]\n'.format(r + 1, 0, v, style)
                else:
                    v = ''
                    for (input_function, (l, row)) in self.get_input_nanowires().items():
                        if r == row and layer == l // 2:
                            v = 'Vin<SUB>{}</SUB>'.format(input_function)
                    layer_content += '\tm{}_{} [label=<{}> {}]\n'.format(r + 1, 0, v, style)

            layer_content += '\n\t// Outputs (right y-axis)\n'

            # Outputs
            output_variables = dict()
            for (o, (l, r)) in self.output_nanowires.items():
                if (l, r) in output_variables:
                    output_variables[(l, r)].append(o)
                else:
                    output_variables[(l, r)] = [o]
            for ((l, r), os) in output_variables.items():
                if layer == l // 2:
                    for i in range(len(os)):
                        v = os[i]
                        style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
                        layer_content += '\tm{}_{} [label="{}" {}];\n'.format(r + 1, self.columns + 1, v, style)

            layer_content += '\n\t// Crossbar\n'
            # Important: The description of the grid is transposed when being rendered -> rows and columns are switched
            for r in range(self.rows):
                layer_content += '\trank=same {\n'
                for c in range(self.columns):
                    if (layer * 2, r) in self.get_input_nanowires().values():
                        layer_content += '\t\tm{}_{} -- m{}_{};\n'.format(r + 1, c, r + 1, c + 1)
                    else:
                        if c == 0:
                            layer_content += '\t\tm{}_{} -- m{}_{} [style=invis];\n'.format(r + 1, c, r + 1, c + 1)
                        else:
                            layer_content += '\t\tm{}_{} -- m{}_{};\n'.format(r + 1, c, r + 1, c + 1)
                        # layer_content += '\t\tm{}_{} -- m{}_{};\n'.format(r + 1, c, r + 1, c + 1)
                    # if (layer // 2, r) not in self.get_input_nanowires().values() or c != 0:
                    #     layer_content += '\t\tm{}_{} -- m{}_{} [style=invis];\n'.format(r + 1, c, r + 1, c + 1)
                    # else:
                    #     layer_content += '\t\tm{}_{} -- m{}_{};\n'.format(r + 1, c, r + 1, c + 1)

                # TODO: Change layer
                if (layer * 2, r) in output_variables:
                    layer_content += '\t\tm{}_{} -- m{}_{};\n'.format(r + 1, self.columns, r + 1, self.columns + 1)
                layer_content += '\t}\n'

            for c in range(self.columns):
                layer_content += '\t' + ' -- '.join(["m{}_{}".format(r + 1, c + 1) for r in range(self.rows)]) + '\n'

            layer_content += '}'

            layer_contents.append(layer_content)

            DotGenerator.generate(benchmark_name + "_" + str(layer), layer_content)

        return layer_contents
