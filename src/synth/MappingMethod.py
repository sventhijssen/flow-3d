from abc import ABC, abstractmethod

from networkx import Graph

from core.MemristorCrossbar import MemristorCrossbar


class MappingMethod(ABC):

    def __init__(self):
        self.crossbar = None
        self.start_time = None
        self.end_time = None
        self.log = ''

    @abstractmethod
    def map(self, graph: Graph) -> MemristorCrossbar:
        pass

    @abstractmethod
    def get_log(self) -> str:
        pass
