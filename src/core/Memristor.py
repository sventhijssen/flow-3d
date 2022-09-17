from core.Literal import Literal


class Memristor:
    """
    A memristor is a programmable device with a resistive state.
    The device can be assigned a Boolean literal, and can consequently be programmed to either a
    low resistive state (ON/True/1) or a high resistive state (OFF/False/0).
    """

    def __init__(self, row: int, column: int, literal: Literal, layer: int = 0, stuck_at_fault: bool = False,
                 permanent: bool = False):
        """
        Constructs a memristor object for given literal at the given row, column, and layer.
        :param row: The given row in the crossbar.
        :param column: The given column in the crossbar.
        :param literal: The given literal to be assigned to this memristor.
        :param layer: The given layer in the crossbar.
        """
        super().__init__()
        self.row = row
        self.column = column
        self.layer = layer
        self.literal = literal
        self.stuck_at_fault = stuck_at_fault
        self.permanent = permanent

    def __str__(self):
        return str(self.literal)

    def __repr__(self):
        return str(self.literal)
