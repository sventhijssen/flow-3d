import math

from networkx import Graph

from aux import config
from core.Literal import Literal
from core.MemristorCrossbar import MemristorCrossbar


class CrossbarMapping3D:

    def __init__(self, graph: Graph, layers: int = 1):
        self.graph = graph
        self.layers = layers
        self.vertical = [[] for layer in range(math.ceil((layers+1)/2))]
        self.horizontal = [[] for layer in range(math.floor((layers+1)/2))]
        self.crossbar = None

    def map(self, labeling):
        input_variables = set()
        input_nodes = dict()
        root_nodes = dict()

        rows = max(1, labeling[0])
        columns = max(1, labeling[1])
        node_assignment = labeling[2]
        edge_assignment = labeling[3]

        q = [[] for layer in range(self.layers + 1)]
        for (node, layers) in node_assignment.items():
            for layer in layers:
                q[layer].append(node)

        crossbar = MemristorCrossbar(rows, columns, layers=self.layers)

        for ((v0, v1), (l0, l1)) in edge_assignment.items():
            if l0 % 2 == 0:
                l = min(l0, l1)
                r = q[l0].index(v0)
                c = q[l1].index(v1)
            else:
                l = min(l0, l1)
                c = q[l0].index(v0)
                r = q[l1].index(v1)
            edge_data = self.graph.get_edge_data(v0, v1)
            variable = edge_data["variable"]
            positive = edge_data["positive"]
            crossbar.set_memristor(r, c, Literal(variable, positive), layer=l)

        # For each node v in layers (l, l+1), we introduce a True value.
        for (node, layers) in node_assignment.items():
            if self.graph.nodes[node]["variable"] != '1' and self.graph.nodes[node]["variable"] != '0':
                input_variables.add(self.graph.nodes[node]["variable"])

            if config.io_constraints:
                if self.graph.nodes[node]["terminal"]:
                    input_variable = self.graph.nodes[node]["variable"]
                    input_nodes[input_variable] = (0, q[0].index(node))
                if self.graph.nodes[node]["root"]:
                    output_variables = self.graph.nodes[node]["output_variables"]
                    for output_variable in output_variables:
                        if config.output_layer is not None:
                            root_nodes[output_variable] = (config.output_layer, q[config.output_layer].index(node))
                        else:
                            if self.layers % 2 == 0:
                                root_nodes[output_variable] = (self.layers, q[self.layers].index(node))
                            else:
                                root_nodes[output_variable] = (self.layers - 1, q[self.layers - 1].index(node))

            sorted(layers)

            for i in range(len(layers) - 1):
                l = layers[i]
                if l % 2 == 0:
                    r = q[l].index(node)
                    c = q[l+1].index(node)
                else:
                    c = q[l].index(node)
                    r = q[l+1].index(node)
                crossbar.set_memristor(r, c, Literal("True", True), layer=l)

        crossbar.input_variables = list(input_variables)
        for (input_function, (layer, nanowire)) in input_nodes.items():
            crossbar.set_input_nanowire(input_function, nanowire, layer=layer)
        for (output_function, (layer, nanowire)) in root_nodes.items():
            crossbar.set_output_nanowire(output_function, nanowire, layer=layer)
        self.crossbar = crossbar

        return self.crossbar
