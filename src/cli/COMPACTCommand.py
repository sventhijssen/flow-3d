import sys

from networkx import DiGraph

from aux import config
from core.MemristorCrossbarTopology import MemristorCrossbarTopology
from synth.COMPACT import COMPACT
from cli.Command import Command


class COMPACTCommand(Command):

    def __init__(self, args: list):
        """
        Command to apply the COMPACT algorithm to a graph.

        :param args: A list of required and optional arguments.

        compact [-gamma|-g VALUE] [-l VALUE] [-vh] [-io] [-r VALUE] [-c VALUE] [-t VALUE]

        Optional arguments:

        -gamma VALUE    Gamma value [0,1].

        -g VALUE        Shorthand for -gamma.

        -l VALUE        The number of layers.

        -t VALUE        Time limit in seconds.

        """

        super(COMPACTCommand).__init__()

        if "-gamma" in args:
            idx = args.index("-gamma")
            config.gamma = float(args[idx + 1])
        else:
            config.gamma = 1

        if "-g" in args:
            idx = args.index("-g")
            config.gamma = float(args[idx + 1])
        else:
            config.gamma = 1

        if "-l" in args:
            idx = args.index("-l")
            self.layers = int(args[idx + 1])
        else:
            self.layers = 1

        if "-vh" in args:
            config.vh_labeling = True
        else:
            config.vh_labeling = False

        if "-io" in args:
            config.io_constraints = False
        else:
            config.io_constraints = True

        if "-r" in args:
            idx = args.index("-r")
            config.max_rows = int(args[idx + 1])
        else:
            config.max_rows = sys.maxsize

        if "-c" in args:
            idx = args.index("-c")
            config.max_columns = int(args[idx + 1])
        else:
            config.max_columns = sys.maxsize

        if "-t" in args:
            idx = args.index("-t")
            config.time_limit = int(args[idx + 1])
        else:
            config.time_limit = None

        if "-obj" in args:
            idx = args.index("-obj")
            config.objective = args[idx + 1]
        else:
            config.objective = "semi"

        if "-alt" in args:
            config.alt_labeling = True
        else:
            config.alt_labeling = False

        if "-keep" in args:
            config.keep_files = True
        else:
            config.keep_files = False

        if "-in" in args:
            idx = args.index("-in")
            config.input_layer = int(args[idx + 1])
        else:
            config.input_layer = None

        if "-out" in args:
            idx = args.index("-out")
            config.output_layer = int(args[idx + 1])
        else:
            config.output_layer = None

    def execute(self):
        """
        Executes the COMPACT algorithm on a graph.
        The graph is obtained from the current context.
        :return:
        """

        context = config.context_manager.get_context()
        compact = COMPACT()
        graphs = context.boolean_function.get_graphs()
        topology_graph = DiGraph()
        # context.crossbars = []
        # for graph in graphs:
        #     context.crossbars.append(compact.map(graph, self.layers))
        for graph in graphs:
            topology_graph.add_node(compact.map(graph, self.layers))
        crossbar_topology = MemristorCrossbarTopology(topology_graph, [])
        config.context_manager.add_context("topology", crossbar_topology)
        return False
