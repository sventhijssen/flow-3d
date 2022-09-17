from pathlib import Path
from typing import List

from aux import config
from aux.BenchmarkReader import BenchmarkReader
from verf.Enumeration import Enumeration
from cli.Command import Command


class EnumerationCommand(Command):

    def __init__(self, args: List[str]):
        super(EnumerationCommand).__init__()
        if len(args) < 1:
            raise Exception("Specification not provided.")
        self.relative_specification_file_path = args[0]

        if "-s" in args:
            idx = args.index("-s")
            self.sampling_size = int(args[idx + 1])
        else:
            self.sampling_size = 0

        if "-pi" in args:
            idx = args.index("-pi")
            self.primary_input_path = Path(args[idx + 1])
        else:
            self.primary_input_path = None

        if "--trace" in args:
            config.trace = True
        else:
            config.trace = False

        if "--verbose" in args:
            config.verbose = True
        else:
            config.verbose = False

    def execute(self):
        context = config.context_manager.get_context()
        crossbar_topology = context.boolean_function

        benchmark_reader = BenchmarkReader(self.relative_specification_file_path)
        benchmark_reader.read()
        context = config.context_manager.get_context()
        benchmark = context.boolean_function

        # TODO: Currently, we assume Verilog code is provided.
        check = Enumeration(crossbar_topology, benchmark)
        check.is_equivalent(None, self.sampling_size)
        return False
