# Base code obtained from:
# https://stackoverflow.com/questions/14080398/z3py-how-to-get-the-list-of-variables-from-a-formula
# Author: Vu Nguyen
# Accessed on: May 8, 2021
#
# Begin code
# Wrapper for allowing Z3 ASTs to be stored into Python Hashtables.
from z3 import is_const, Z3_OP_UNINTERPRETED, is_not, AstRef


class AstRefKey:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return self.n.hash()

    def __eq__(self, other):
        return self.n.eq(other.n)

    def __repr__(self):
        return str(self.n)


def _askey(n):
    assert isinstance(n, AstRef)
    return AstRefKey(n)


def get_literals(f):
    if isinstance(f, bool):
        return [f]
    r = []

    def collect(f):
        if is_const(f):
            if f.decl().kind() == Z3_OP_UNINTERPRETED:
                r.append(_askey(f))
        elif is_not(f):
            for c in f.children():
                if c.decl().kind() == Z3_OP_UNINTERPRETED:
                    r.append(_askey(f))
        else:
            for c in f.children():
                collect(c)

    collect(f)
    return r

# End code
