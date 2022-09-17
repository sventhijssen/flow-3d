from typing import List

from aux import config
from cli.Command import Command
from aux.ROBDDDOTParser import ROBDDDOTParser
from aux.SBDDDOTParser import SBDDDOTParser


class BDDCommand(Command):

    def __init__(self, bdd_type: str, args: List[str]):
        """A BDDCommand
        :param bdd_type:
        :param args:
        """
        super(BDDCommand).__init__()

        self.bdd_type = bdd_type
        config.bdd = bdd_type

        if "-all" in args or "-a" in args:
            config.full_bdd = True
        else:
            config.full_bdd = False

        if "-t" in args:
            idx = args.index("-t")
            config.time_limit_bdd = int(args[idx + 1])
        else:
            config.time_limit_bdd = 24 * 60 * 60  # 24 hours

        if "-m" in args:
            self.merge = True
        else:
            self.merge = False

        if "-keep" in args:
            self.keep = True
        else:
            self.keep = False

        if "!h" in args:
            config.heuristic = False
        else:
            config.heuristic = True

        self.args = args

    def execute(self):
        context = config.context_manager.get_context()

        # Reduced Ordered Binary Decision Diagram
        if self.bdd_type == "bdd":
            robdd_parser = ROBDDDOTParser(context.boolean_function)
            robdd = robdd_parser.parse()
            sbdd_parser = SBDDDOTParser(context.boolean_function)
            sbdd = sbdd_parser.parse()
            raise Exception("Unsupported")

            # if self.merge:
            #     robdd.merge()
            #     sbdd.merge()
            #
            #     if len(robdd.nodes) < len(sbdd.nodes):
            #         config.bdd_parser = robdd_parser
            #         context.benchmark_graph = robdd
            #         config.bdd = 'robdd'
            #     else:
            #         config.bdd_parser = sbdd_parser
            #         context.benchmark_graph = sbdd
            #         config.bdd = 'sbdd'
            # else:
            #     if len(robdd.nodes) < len(sbdd.nodes):
            #         config.bdd_parser = robdd_parser
            #         context.benchmark_graph = robdd
            #         config.bdd = 'robdd'
            #     else:
            #         config.bdd_parser = sbdd_parser
            #         context.benchmark_graph = sbdd
            #         config.bdd = 'sbdd'
        elif self.bdd_type == "robdd":
            config.bdd_parser = ROBDDDOTParser(context.boolean_function)
            benchmark_graph = config.bdd_parser.parse()
            config.context_manager.add_context("", benchmark_graph)
            context = config.context_manager.get_context()
            if self.merge:
                context.boolean_function.merge()

        # Shared Binary Decision Diagram
        elif self.bdd_type == "sbdd":
            config.bdd_parser = SBDDDOTParser(context.boolean_function)
            benchmark_graph = config.bdd_parser.parse()
            config.context_manager.add_context("", benchmark_graph)
            context = config.context_manager.get_context()
            if self.merge:
                context.boolean_function.merge()
        else:
            raise Exception("Unsupported BDD type.")

        return False
