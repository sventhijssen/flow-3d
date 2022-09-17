from aux import config
from cli.Command import Command


class DrawMatrixCommand(Command):

    def __init__(self, args: list):
        super(DrawMatrixCommand).__init__()
        if len(args) > 0:
            self.name = args[0]
        else:
            raise Exception("Name must be provided.")

        if "-latex" in args or "-L" in args:
            self.draw_latex = True
        else:
            self.draw_latex = False

    def execute(self):
        context = config.context_manager.get_context()
        boolean_function = context.boolean_function
        boolean_function.draw_matrix(self.name, self.draw_latex)
        return False
