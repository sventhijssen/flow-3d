from core.BooleanFunction import BooleanFunction
from core.Literal import Literal
from core.MemristorCrossbar import MemristorCrossbar


class CrossbarWriter:

    def __init__(self, boolean_function: BooleanFunction, file_name: str):
        self.boolean_function = boolean_function
        self.file_name = file_name

    def write(self):
        with open(self.file_name, 'w') as f:
            f.write(self.boolean_function.write_xbar())
            # for crossbar in self.crossbar:
            #     f.write(".model {}\n".format(self.file_name))
            #     f.write(".inputs {}\n".format(' '.join(crossbar.get_input_variables())))
            #     f.write(".outputs {}\n".format(' '.join(crossbar.get_output_variables())))
            #     f.write(".rows {}\n".format(crossbar.rows))
            #     f.write(".columns {}\n".format(crossbar.columns))
            #     for (input_variable, (layer, nanowire)) in crossbar.get_input_nanowires().items():
            #         if crossbar.layers == 1:
            #             f.write(".i {} {}\n".format(input_variable, nanowire))
            #         else:
            #             f.write(".i {} {} {}\n".format(input_variable, nanowire, layer))
            #     for (output_variables, (layer, nanowire)) in crossbar.get_output_nanowires().items():
            #         if crossbar.layers == 1:
            #             if isinstance(output_variables, str):
            #                 f.write(".o {} {}\n".format(output_variables, nanowire))
            #             else:
            #                 f.write(".o {} {}\n".format(" ".join(output_variables), nanowire))
            #         else:
            #             if isinstance(output_variables, str):
            #                 f.write(".o {} {} {}\n".format(output_variables, nanowire, layer))
            #             else:
            #                 f.write(".o {} {} {}\n".format(" ".join(output_variables), nanowire, layer))
            #     f.write(".xbar\n")
            #     for r in range(crossbar.rows):
            #         for c in range(crossbar.columns):
            #             literal = self._literal_representation(crossbar.get_memristor(r, c).literal)
            #             if c < crossbar.columns - 1:
            #                 f.write("{}\t".format(literal))
            #             else:
            #                 f.write("{}\r\n".format(literal))
            #     f.write(".end\n")
