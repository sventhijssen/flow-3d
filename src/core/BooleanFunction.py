from abc import ABC, abstractmethod
from typing import Dict, Set


class BooleanFunction(ABC):

    def __init__(self, name: str = "", input_variables=None, output_variables=None):
        self.name = name
        self.input_variables = input_variables
        self.output_variables = output_variables

    def get_input_variables(self) -> Set[str]:
        return self.input_variables

    def get_output_variables(self) -> Set[str]:
        return self.output_variables

    @abstractmethod
    def write_xbar(self) -> str:
        pass

    @abstractmethod
    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        pass
