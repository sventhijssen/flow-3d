from aux import config
from cli.Command import Command


class WriteLogCommand(Command):

    def __init__(self, args):
        super(WriteLogCommand).__init__()
        if len(args) < 1:
            raise Exception("No filename defined.")
        self.file_name = args[0]

    def execute(self) -> bool:
        config.log.write(self.file_name)
        return False
