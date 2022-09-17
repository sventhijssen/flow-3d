import itertools
import math
import random
import time
from pathlib import Path

from z3 import Bool

from core.Benchmark import Benchmark
from core.BooleanFunction import BooleanFunction
from verf.EquivalenceChecker import EquivalenceChecker
from aux.Z3Converter import Z3Converter
from core.Literal import Literal


class Enumeration(EquivalenceChecker):

    def __init__(self, boolean_function_a: BooleanFunction, boolean_function_b: BooleanFunction,
                 primary_input_path: Path = None):
        super().__init__(boolean_function_a, boolean_function_b)
        # TODO: Fix primary inputs
        self.primary_input_map = self._read_primary_input_map(primary_input_path)

    @staticmethod
    def _read_primary_input_map(primary_input_path: Path):
        primary_input_map = dict()

        if primary_input_path is None:
            return

        with open(str(primary_input_map), 'r') as f:
            for line in f.readlines():
                new, old = line.split()
                primary_input_map[old] = new

        return primary_input_map

    def is_equivalent(self, benchmark: Benchmark, sampling_size: int = 0) -> bool:
        print("Started enumeration")
        start_time = time.time()

        input_variables_a = set(self.boolean_function_a.get_input_variables())
        input_variables_b = set(self.boolean_function_b.get_input_variables())

        input_variables = list(input_variables_a.union(input_variables_b))

        output_variables_a = set(self.boolean_function_a.get_output_variables())
        output_variables_b = set(self.boolean_function_b.get_output_variables())
        output_variables = list(output_variables_a.union(output_variables_b))

        n = len(input_variables)

        if sampling_size == 0:
            for i in range(int(math.pow(2, n))):
                print("\t{}/{}".format(i + 1, int(math.pow(2, n))))
                binary_string = format(int(i), '0' + str(n) + 'b')
                instance = {}
                for j in range(n):
                    input_variable = input_variables[j]
                    instance[input_variable] = bool(int(binary_string[n - j - 1]))
                # print(instance)

                evaluation_a = self.boolean_function_a.eval(instance)
                evaluation_b = self.boolean_function_b.eval(instance)

                for output_variable in output_variables:
                    if evaluation_a[output_variable] != evaluation_b[output_variable]:
                        print("Not equivalent.")
                        print(output_variable)
                        print(instance)
                        print(evaluation_a[output_variable])
                        print(evaluation_b[output_variable])
                        print("Stopped enumeration")
                        print()
                        return False
        else:
            for i in range(sampling_size):
                r = random.randint(0, int(math.pow(2, n)))
                print("\t{}/{}".format(i + 1, sampling_size))
                binary_string = format(int(r), '0' + str(n) + 'b')
                instance = {}
                for j in range(n):
                    input_variable = input_variables[j]
                    instance[input_variable] = bool(int(binary_string[n - j - 1]))
                # print(instance)

                evaluation_a = self.boolean_function_a.eval(instance)
                evaluation_b = self.boolean_function_b.eval(instance)

                for output_variable in output_variables:
                    if evaluation_a[output_variable] != evaluation_b[output_variable]:
                        print("Not equivalent.")
                        print(output_variable)
                        print(instance)
                        print(evaluation_a[output_variable])
                        print(evaluation_b[output_variable])
                        print("Stopped enumeration")
                        print()
                        return False

        print("Equivalent.")
        print("Stopped enumeration")
        print()
        return True

    def to_formula(self, output_variable: str) -> Bool:
        truth_table = list(map(lambda x: list(x), list(
            itertools.product([False, True], repeat=len(self.boolean_function_a.input_variables)))))

        simple_paths = []
        for instance_list in truth_table:
            instance = dict(zip(self.boolean_function_a.input_variables, instance_list))
            crossbar_evaluations = self.boolean_function_a.eval(instance)
            if crossbar_evaluations[output_variable]:
                simple_path = [
                    str(Literal(self.boolean_function_a.input_variables[i], instance_list[i])).replace('\\+', '~') for i
                    in range(len(self.boolean_function_a.input_variables))]
                simple_paths.append(simple_path)

        self.simple_paths[output_variable] = simple_paths

        formula = Z3Converter.simple_paths_to_z3(simple_paths)
        self.formulae[output_variable] = formula

        return formula
