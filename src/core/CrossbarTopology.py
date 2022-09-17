from abc import abstractmethod
from typing import Dict

from core.BooleanFunction import BooleanFunction


class CrossbarTopology(BooleanFunction):

    @abstractmethod
    def write_xbar(self) -> str:
        pass

    @abstractmethod
    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        pass

    @abstractmethod
    def draw_matrix(self, name: str, draw_latex: bool = False):
        pass

    @abstractmethod
    def draw_graph(self, name: str):
        pass
