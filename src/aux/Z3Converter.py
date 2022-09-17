import re
from typing import List

from pyparsing import Suppress, Forward, Word, Group, ZeroOrMore, alphanums, oneOf, Literal
from z3 import Or, And, Xor, If, Not, Bool, is_app_of, Z3_OP_XOR, Z3_OP_UNINTERPRETED, is_const, is_not, AstRef, is_and, \
    is_or, ExprRef, set_option


class AstRefKey:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return self.n.hash()

    def __eq__(self, other):
        return self.n.eq(other.n)

    def __repr__(self):
        return str(self.n)


class Z3Converter:

    @staticmethod
    def simple_paths_to_z3(one_paths: List[List[str]]) -> Bool:
        """
        Returns a formula in Verilog to a formula compatible with Z3.
        :param one_paths:
        :return:
        """

        products = []
        for one_path in one_paths:
            product = []
            for raw_literal in one_path:
                literal = str(raw_literal).replace('\\+', '~')
                if literal.startswith('~'):
                    product.append(Not(Bool(literal.replace('~', ''))))
                else:
                    if literal == "True":
                        product.append(True)
                    else:
                        product.append(Bool(literal))
            products.append(And(product))

        formula = Or(products)

        return formula

    @staticmethod
    def _converted_formula_tree(lst):
        """
        Returns a formula in Verilog to a formula compatible with Z3.
        :param lst:
        :return:
        """
        if not lst:
            return Or()

        if isinstance(lst, str):
            if lst[0] == '~':
                return Not(Bool(lst[1:]))
            return Bool(lst)
        if len(lst) == 1:
            return Z3Converter._converted_formula_tree(lst[0])
        elif len(lst) >= 3 and lst[1] == '^':
            expressions = [lst[i] for i in range(0, len(lst), 2)]
            z3_expressions = list(map(lambda e: Z3Converter._converted_formula_tree(e), expressions))
            return Xor(*z3_expressions)
        elif len(lst) >= 3 and lst[1] == '&':
            expressions = [lst[i] for i in range(0, len(lst), 2)]
            z3_expressions = list(map(lambda e: Z3Converter._converted_formula_tree(e), expressions))
            return And(*z3_expressions)
        elif len(lst) >= 3 and lst[1] == '|':
            expressions = [lst[i] for i in range(0, len(lst), 2)]
            z3_expressions = list(map(lambda e: Z3Converter._converted_formula_tree(e), expressions))
            return Or(*z3_expressions)
        elif len(lst) >= 5 and lst[1] == '?':
            cond = lst[0]
            true_stmt = lst[2]
            false_stmt = lst[4]
            return If(Z3Converter._converted_formula_tree(cond), Z3Converter._converted_formula_tree(true_stmt), Z3Converter._converted_formula_tree(false_stmt), ctx=None)

        return

    @staticmethod
    def verilog_to_tree(verilog_formula: str):
        # Begin Source
        # URL: https://stackoverflow.com/questions/37925803/parserelement-enablepackrat-doesnt-make-infixnotation-faster
        # Author: PaulMcG
        # Published on: June 20, 2016
        # Accessed on: July 15, 2020
        # Begin Source (2): https://stackoverflow.com/questions/23879784/parse-mathematical-expressions-with-pyparsing
        # Author: PaulMcG
        # Published on: May 20, 2014
        # Visited on: July 15, 2020
        LPAR, RPAR = map(Suppress, '()')
        expr = Forward()
        variable = Word(alphanums + '_~' '[' ']')
        nested = variable | Group(LPAR + expr + RPAR)
        binary_op = nested + ZeroOrMore(oneOf('^ | &') + nested)
        ternary_op = nested + Literal('?') + nested + Literal(':') + nested
        formula_expr = ternary_op | binary_op
        expr <<= formula_expr
        verilog_tree = [expr.parseString(verilog_formula).asList()]
        # End Source

        return verilog_tree

    @staticmethod
    def verilog_to_z3(verilog_formula: str):
        if verilog_formula == "1\'b0":
            return False
        elif verilog_formula == "1\'b1":
            return True
        else:
            verilog_tree = Z3Converter.verilog_to_tree(verilog_formula)
            z3_formula = Z3Converter._converted_formula_tree(verilog_tree)
            return z3_formula

    @staticmethod
    def _is_xor(a):
        return is_app_of(a, Z3_OP_XOR)

    @staticmethod
    def _askey(n):
        assert isinstance(n, AstRef)
        return AstRefKey(n)

    @staticmethod
    def _collect(f: Bool) -> str:
        if f is None:
            return ""
        if is_const(f):
            if f.decl().kind() == Z3_OP_UNINTERPRETED:
                return str(Z3Converter._askey(f))
            else:
                return str(f)
        elif is_not(f):
            s = "~"
            for c in f.children():
                s += Z3Converter._collect(c)
            return s
        elif is_and(f):
            return "(" + " & ".join([str(Z3Converter._collect(c)) for c in f.children()]) + ")"
        elif is_or(f):
            return "(" + " | ".join([str(Z3Converter._collect(c)) for c in f.children()]) + ")"
        elif Z3Converter._is_xor(f):
            return "(" + " ^ ".join([str(Z3Converter._collect(c)) for c in f.children()]) + ")"
        elif isinstance(f, ExprRef): # IF statement
            children = list(map(lambda e: Z3Converter._collect(e), f.children()))
            return "(({}) ? ({}) : ({}))".format(children[0], children[1], children[2])
        else:
            raise Exception("Unexpected operator.")

    @staticmethod
    def z3_to_verilog(z3_formula: Bool) -> str:
        return Z3Converter._collect(z3_formula)

    @staticmethod
    def z3_to_str(z3_formula: Bool) -> str:
        set_option(max_args=1000000000000, max_lines=100000000000, max_depth=1000000000000, max_visited=100000000000)
        return str(z3_formula)

    @staticmethod
    def str_to_z3(str_formula: str) -> Bool:
        set_option(max_args=1000000000000, max_lines=100000000000, max_depth=1000000000000, max_visited=100000000000)
        keywords = ["And", "Or", "Xor", "Not", "If", "True", "False"]
        stripped_formula = str_formula
        stripped_formula = re.sub('[^0-9a-zA-Z]+', ' ', stripped_formula)
        for keyword in keywords:
            stripped_formula = stripped_formula.replace(keyword, " ")
        input_variables = set(stripped_formula.split(" "))
        input_variables.remove("")
        input_variables = list(input_variables)
        for input_variable in input_variables:
            exec_str = "{} = Bool('{}')".format(input_variable, input_variable)
            exec(exec_str)
        str_formula = re.sub(r"((?:Or|And|Not|Xor|If)(?!\s*\())", r"\1(False)", str_formula)
        # remove_empty_operators(str_formula)
        # print(str_formula)
        return eval(str_formula)
