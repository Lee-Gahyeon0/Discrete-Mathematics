from typing import Set, Tuple, Union

Expr = Union[str, Tuple[str, str]]


def is_atom(value):
    return isinstance(value, str)


def is_not(value):
    # === QUIZ: implement NOT predicate detection ===
    raise NotImplementedError("QUIZ: is_not needs implementation")


def is_lit(value):
    # === QUIZ: determine if a value is a literal (atom or NOT(atom)) ===
    raise NotImplementedError("QUIZ: is_lit needs implementation")


def negate(literal):
    # === QUIZ: return the logical negation of a literal ===
    raise NotImplementedError("QUIZ: negate needs implementation")


class KB:
    def __init__(self):
        self.facts: Set[Expr] = set()

    def add_fact(self, fact: Expr) -> bool:
        # === QUIZ: validate and insert a literal fact into the KB ===
        raise NotImplementedError("QUIZ: add_fact needs implementation")