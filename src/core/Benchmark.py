from pathlib import Path
from typing import Dict, List

from core.BooleanFunction import BooleanFunction
from core.Formula import Formula


class Benchmark(BooleanFunction):

    def __init__(self, file_path: Path, input_variables: List[str], output_variables: List[str],
                 formulas: Dict[str, Formula] = None):
        super(Benchmark).__init__()
        if file_path is not None:
            [name, _] = file_path.name.split('.')
            self.name = name
        else:
            self.name = ""
        self.model = self.name
        self.file_path = file_path
        self.input_variables = input_variables
        self.output_variables = output_variables
        if formulas is None:
            self.formulas = dict()
        else:
            self.formulas = formulas
        self.graph = None

    def get_graphs(self):
        return self.graph

    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        evaluation = dict()
        for (output_variable, formula) in self.formulas.items():
            evaluation[output_variable] = formula.eval(instance)
        return evaluation

    def write_xbar(self) -> str:
        raise TypeError()

    def __str__(self):
        return self.name + ""

    def add_formula(self, formula):
        self.formulas[formula.output_variable] = formula
