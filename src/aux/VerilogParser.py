import re

from aux.BenchmarkParser import BenchmarkParser
from core.Formula import Formula
from core.VerilogBenchmark import VerilogBenchmark


class VerilogParser(BenchmarkParser):

    def parse(self) -> VerilogBenchmark:
        # TODO: Find a better solution for handling these arrays
        self.content = self.content.replace('\\', '').replace('[', '').replace(']', '')

        with open(self.file_path, 'w') as f:
            f.write(self.content)

        matches = re.findall(r'module\s+(.+)\s+\(', self.content)
        module_name = matches[0].replace(' ', '')

        match = re.search(r'input([.\r\n]*[^;])+', self.content)
        raw_input_variables = match.group()
        all_input_variables = raw_input_variables.replace('input', '').replace('\n', ' ').replace(' ', '').split(',')

        match = re.search(r'output([.\r\n]*[^;])+', self.content)
        raw_output_variables = match.group()
        output_variables = raw_output_variables.replace('output', '').replace('\n', ' ').replace(' ', '').split(',')

        match = re.search(r'wire([.\r\n]*[^;])+', self.content)
        if match:
            raw_auxiliary_variables = match.group()
            auxiliary_variables = raw_auxiliary_variables.replace('wire', '').replace('\n', ' ').replace(' ', '').split(',')
        else:
            auxiliary_variables = []

        assignments = re.findall(r'assign\s+(.+)\s+=\s+(.+);', self.content)

        functions = dict()
        for (raw_function_name, raw_formula) in assignments:
            function_name = raw_function_name.replace(' ', '')
            formula = Formula([], function_name, raw_formula)
            functions[function_name] = formula

        self.benchmark = VerilogBenchmark(self.file_path, module_name, all_input_variables, output_variables, functions, auxiliary_variables)

        return self.benchmark
