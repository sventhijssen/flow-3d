from cli.BDDCommand import BDDCommand
from cli.COMPACTCommand import COMPACTCommand
from cli.ChakrabortyCommand import ChakrabortyCommand
from cli.DrawGraphCommand import DrawGraphCommand
from cli.DrawMatrixCommand import DrawMatrixCommand
from cli.EnumerationCommand import EnumerationCommand
from cli.EvalCommand import EvalCommand
from cli.ExitCommand import ExitCommand
from cli.ListCommand import ListCommand
from cli.NewLogCommand import NewLogCommand
from cli.ReadBDDCommand import ReadBDDCommand
from cli.ReadCommand import ReadCommand
from cli.ReadCrossbarCommand import ReadCrossbarCommand
from cli.SwitchContextCommand import SwitchContextCommand
from cli.WriteBDDCommand import WriteBDDCommand
from cli.WriteCrossbarCommand import WriteCrossbarCommand
from cli.WriteLogCommand import WriteLogCommand


class CommandParser:

    @staticmethod
    def parse(raw_command: str):
        """
        Parses the given command. The command is split into tokens by a whitespace.
        The first token is the command name, upon which the correct command is called with the respective arguments.
        :param raw_command: A command in the format of one string.
        :return: Returns the command based on the first token in the given command string.

        These commands are:

        - exit
        - read
        - bdd
        - robdd
        - sbdd
        - read_bdd
        - write_bdd
        - compact
        - path
        - chakraborty
        - draw
        - draw_matrix
        - draw_graph
        - ls

        """
        command_list = raw_command.strip().split(" ")
        command_name = command_list[0]
        args = command_list[1:]
        if command_name == "exit":
            return ExitCommand()
        elif command_name == "read":
            return ReadCommand(args)
        elif command_name == "bdd":
            return BDDCommand("bdd", args)
        elif command_name == "robdd":
            return BDDCommand("robdd", args)
        elif command_name == "sbdd":
            return BDDCommand("sbdd", args)
        elif command_name == "read_bdd":
            return ReadBDDCommand(args)
        elif command_name == "write_bdd":
            return WriteBDDCommand(args)
        elif command_name == "compact":
            return COMPACTCommand(args)
        elif command_name == "chakraborty":
            return ChakrabortyCommand()
        elif command_name == "draw":
            return DrawMatrixCommand(args)
        elif command_name == "draw_matrix":
            return DrawMatrixCommand(args)
        elif command_name == "draw_graph":
            return DrawGraphCommand(args)
        elif command_name == "ls":
            return ListCommand(args)
        elif command_name == "switch":
            return SwitchContextCommand(args)
        elif command_name == "eval":
            return EvalCommand(args)
        elif command_name == "enum":
            return EnumerationCommand(args)
        elif command_name == "new_log":
            return NewLogCommand(args)
        elif command_name == "write_log":
            return WriteLogCommand(args)
        elif command_name == "write_xbar":
            return WriteCrossbarCommand(args)
        elif command_name == "read_xbar":
            return ReadCrossbarCommand(args)
        else:
            raise Exception("Unknown command.")
