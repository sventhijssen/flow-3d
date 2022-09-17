from aux import config
from synth.ChakrabortyMappingMethod import ChakrabortyMappingMethod
from cli.Command import Command


class ChakrabortyCommand(Command):

    def __init__(self):
        super(ChakrabortyCommand).__init__()

    def execute(self):
        context = config.context_manager.get_context()
        chakraborty = ChakrabortyMappingMethod()
        graphs = context.benchmark_graph.get_graphs()
        context.crossbars = []
        for graph in graphs:
            context.crossbars.append(chakraborty.map(graph))
        return False
