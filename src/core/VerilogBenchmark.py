from pathlib import Path
from typing import Dict, List

from core.BooleanFunction import BooleanFunction
from core.Formula import Formula


class VerilogBenchmark(BooleanFunction):

    def __init__(self, file_path: Path, module_name: str, input_variables: List[str], output_variables: List[str],
                 functions: Dict[str, Formula], auxiliary_variables: List[str] = None):
        super().__init__(module_name, input_variables, output_variables)
        self.file_path = file_path
        self.module_name = module_name
        self.input_variables = input_variables
        self.output_variables = output_variables
        self.functions = functions
        self.auxiliary_variables = auxiliary_variables

    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        evaluation = dict()
        for (output_variable, formula) in self.functions.items():
            evaluation[output_variable] = formula.eval(instance)
        return evaluation

    def write(self, filename: Path):
        input_variables = ", ".join(self.input_variables)
        output_variables = ", ".join(self.output_variables)

        content = "module {} (".format(self.module_name)
        content += "\n"
        content += "\t{}, {});".format(input_variables, output_variables)
        content += "\n"
        content += "\tinput {};".format(input_variables)
        content += "\n"
        content += "\toutput {};".format(output_variables)
        content += "\n"
        if len(self.auxiliary_variables) > 0:
            auxiliary_variables = ", ".join(self.auxiliary_variables)
            content += "\twire {};".format(auxiliary_variables)
            content += "\n"
        for function_name, formula in self.functions.items():
            content += "\tassign {} = {};".format(function_name, formula.verilog)
            content += "\n"
        content += "endmodule"

        with open(filename, 'w') as f:
            f.write(content)

    def write_xbar(self) -> str:
        raise TypeError()
