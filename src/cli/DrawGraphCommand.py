from aux import config
from cli.Command import Command


class DrawGraphCommand(Command):

    def __init__(self, args: list):
        super().__init__()
        self.args = args

        if len(args) > 0:
            self.name = args[0]
        else:
            raise Exception("Name must be provided.")

    def execute(self):
        context = config.context_manager.get_context()
        context.boolean_function.draw_graph(self.name)
        return False
