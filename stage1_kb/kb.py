from typing import Set, Tuple, Union

Expr = Union[str, Tuple[str, str]]


def is_atom(value):
    return isinstance(value, str)


def is_not(value):
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and value[0] == "NOT"
        and isinstance(value[1], str)
    )


def is_lit(value):
    return is_atom(value) or is_not(value)


def negate(literal):
    assert is_lit(literal)
    return literal[1] if is_not(literal) else ("NOT", literal)


class KB:
    def __init__(self):
        self.facts: Set[Expr] = set()

    def add_fact(self, fact: Expr) -> bool:
        if not is_lit(fact):
            raise ValueError("Only atom or NOT(atom) literals are allowed")
        if fact in self.facts:
            return False
        if negate(fact) in self.facts:
            raise ValueError("Contradiction detected")
        self.facts.add(fact)
        return True