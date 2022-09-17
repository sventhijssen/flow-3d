import re
from typing import Dict

from aux.PythonConverter import PythonConverter


class Formula:

    def __init__(self, input_variables, output_variable, verilog):
        self.input_variables = input_variables
        self.output_variable = output_variable
        self.verilog = verilog

    def eval(self, instance: Dict[str, bool]):
        formula_instance = PythonConverter.verilog_to_python_string(self.verilog)

        for (input_variable, value) in instance.items():
            # formula_instance = formula_instance.replace(input_variable, str(value))
            formula_instance = re.sub(r'\b%s\b' % input_variable, str(value), formula_instance)
        return eval(formula_instance)

    def __str__(self):
        return self.output_variable + ' = ' + self.verilog

    def __repr__(self):
        return str(self)
