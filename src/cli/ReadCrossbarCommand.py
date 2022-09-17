from aux import config
from aux.CrossbarReader import CrossbarReader
from cli.Command import Command


class ReadCrossbarCommand(Command):

    def __init__(self, args):
        super(ReadCrossbarCommand).__init__()
        if len(args) < 1:
            raise Exception("Name for crossbar must be defined.")
        if len(args) < 2:
            raise Exception("File name must be defined.")
        self.name = args[0]
        self.file_name = args[1]

    def execute(self) -> bool:
        cr = CrossbarReader(self.file_name)
        crossbar = cr.read()
        config.context_manager.add_context(self.name, crossbar)
        print("Reading completed.")
        return False
