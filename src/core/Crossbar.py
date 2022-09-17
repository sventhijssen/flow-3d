from __future__ import annotations

from abc import abstractmethod
from typing import Dict, Tuple, Set

from networkx import Graph

from core.BooleanFunction import BooleanFunction
from core.Memristor import Memristor
from core.Literal import Literal


class Crossbar(BooleanFunction):
    """
    Abstract class for a crossbar.
    """

    def __str__(self):
        return str(self.matrix)

    def __repr__(self):
        return str(self.matrix)

    def __copy__(self):
        pass

    @abstractmethod
    def draw_matrix(self, benchmark_name: str, draw_latex: bool = False):
        pass

    @abstractmethod
    def draw_latex_matrix(self, benchmark_name: str):
        pass

    @abstractmethod
    def draw_dot_matrix(self, benchmark_name: str):
        pass

    @abstractmethod
    def draw_graph(self, benchmark_name: str):
        pass

    @abstractmethod
    def eval(self, instance: Dict[str, bool], input_function: str = "1") -> Dict[str, bool]:
        pass

    def instantiate(self, instance: Dict) -> Crossbar:
        pass

    @abstractmethod
    def get_matrix(self):
        pass

    def __init__(self, rows: int, columns: int, layers: int = 1, default_literal=Literal("False", False),
                 compressed: bool = False):
        """
        Constructs a crossbar with the given dimensions x, y, and optionally z.
        :param rows: The number of memristors along the input and output nanowires.
        :param columns: The number of memristors orthogonal to the input and output nanowires.
        :param layers: The number of layers of memristors. The number of layers of nanowires is equal to the number
        of layers of memristors plus one. By default, the number of layers = 1.
        """
        super(Crossbar).__init__()
        self.filename = ""
        self.rows = rows
        self.columns = columns
        self.layers = layers
        self.input_nanowires = dict()
        # self.set_input_nanowire("1", self.rows - 1)
        self.output_nanowires = dict()
        # self.set_output_nanowire("f", self.rows - 1, layer=self.get_nanowire_layers() - 1)
        # self.input_nanowires = {"1": self.rows - 1}
        self.input_variables = []
        self.default_literal = default_literal
        self.compressed = compressed

        if self.compressed:
            self.matrix = dict()
        else:
            self.matrix = [[[Memristor(r, c, default_literal, l) for c in range(self.columns)] for r in range(self.rows)] for l in range(self.layers)]

    def set_name(self, name: str):
        self.name = name

    def get_name(self):
        return self.name

    def get_input_nanowire(self, input_function: str) -> Tuple[int, int]:
        return self.input_nanowires[input_function]

    def get_input_nanowires(self) -> Dict[str, Tuple[int, int]]:
        return self.input_nanowires

    def get_output_nanowire(self, output_function: str) -> Tuple[int, int]:
        return self.output_nanowires[output_function]

    def get_output_nanowires(self) -> Dict[str, Tuple[int, int]]:
        return self.output_nanowires

    def set_input_nanowire(self, input_function: str, nanowire: int, layer: int = 0):
        self.input_nanowires[input_function] = (layer, nanowire)

    def set_output_nanowire(self, output_function: str, nanowire: int, layer: int = 0):
        self.output_nanowires[output_function] = (layer, nanowire)

    def get_input_variables(self) -> Set[str]:
        return set(self.input_variables)

    def get_output_variables(self) -> Set[str]:
        return set(self.output_nanowires.keys())

    def graph(self) -> Graph:
        """
        Returns a graph representation based on the following analogy: nanowires in the crossbar correspond to nodes in the graph, and memristors in the crossbar correspond to edges in the graph.
        The resulting graph is a multi-layered graph. More specifically, the graph is k-layered and bipartite.
        :return: A k-layered bipartite graph.
        """
        graph = Graph()
        for layer in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    memristor = self.get_memristor(r, c, layer=layer)
                    if layer % 2 == 0:
                        graph.add_edge("L{}_{}".format(layer, r), "L{}_{}".format(layer + 1, c),
                                       atom=memristor.literal.atom,
                                       positive=memristor.literal.positive)
                    else:
                        graph.add_edge("L{}_{}".format(layer, c), "L{}_{}".format(layer + 1, r),
                                       atom=memristor.literal.atom,
                                       positive=memristor.literal.positive)
        return graph

    def find(self, literal: Literal) -> Set[Tuple[int, int, int]]:
        """
        Returns the positions of the given literals occurring in this crossbar.
        :param literal: The given literal to find in this crossbar.
        :return: A list of positions (tuples) at which the literal occurs.
        """
        positions = set()
        for l in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    if self.get_memristor(r, c, layer=l).literal == literal:
                        positions.add((l, r, c))
        return positions

    def get_rows(self) -> int:
        """
        Returns the number of rows of this crossbar.
        :return: The number of rows of this crossbar.
        """
        return self.rows

    def get_columns(self) -> int:
        """
        Returns the number of columns of this crossbar.
        :return: The number of columns of this crossbar.
        """
        return self.columns

    def get_nanowire_layers(self) -> int:
        """
        Returns the number of layers (nanowires) of this crossbar.
        :return: The number of layers of nanowires in this crossbar.
        """
        return self.layers + 1

    def get_memristor_layers(self) -> int:
        """
        Returns the number of layers (memristors) of this crossbar.
        :return: The number of layers of memristors in this crossbar.
        """
        return self.layers

    def get_semiperimeter(self):
        """
        TODO: Redefine semiperimeter for 3D
        Returns the semiperimeter (number of wordlines + number of bitlines + number of layers of memristors)
        of this crossbar.
        :return: The semiperimeter of this crossbar.
        """
        return self.get_rows() + self.get_columns()

    def get_area(self):
        """
        Returns the area (number of wordlines * number of bitlines) of this crossbar.
        :return: The area of this crossbar.
        """
        return self.get_rows() * self.get_columns()

    def get_volume(self):
        """
        Returns the volume (area * number of layers of memristors) of this crossbar.
        :return: The number of layers of this crossbar.
        """
        return self.get_area() * self.get_memristor_layers()

    def get_memristor(self, row: int, column: int, layer: int = 0) -> Memristor:
        """
        Returns the memristor at the given row and column.
        :param row: The given row in this crossbar.
        :param column: The given column in this crossbar.
        :param layer: The given layer in this crossbar.
        :return: The memristor at the given row and column.
        """
        # TODO: Replace matrix with dictionary to avoid double bookkeeping
        # if (layer, row, column) in self.dictionary:
        #     return self.dictionary[(layer, row, column)]
        # return Memristor(row, column, self.default_literal, layer)
        return self.matrix[layer][row][column]

    def set_memristor(self, row: int, column: int, literal: Literal, layer: int = 0, stuck_at_fault: bool = False,
                      permanent: bool = False):
        """
        TODO: Change double bookkeeping in matrix and dictionary
        Assigns the given literal to the memristor at the given row and column.
        :param row: The given row in this crossbar.
        :param column: The given column in this crossbar.
        :param literal: The given literal to be assigned.
        :param layer: The given layer in this crossbar.
        :param permanent:
        :param stuck_at_fault:
        :return:
        """
        memristor = Memristor(row, column, literal, layer, stuck_at_fault, permanent)
        if self.compressed:
            self.matrix[(layer, row, column, layer)] = memristor
        else:
            self.matrix[layer][row][column] = memristor
        # if literal != self.default_literal and not stuck_at_fault and not permanent:
        #     self.dictionary[(layer, row, column)] = memristor

    @abstractmethod
    def merge(self) -> Crossbar:
        pass
