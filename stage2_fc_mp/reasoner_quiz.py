from typing import List, Set, Tuple, Union

Expr = Union[str, Tuple[str, str]]
Rule = Tuple[str, Expr, Expr]


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
    # === QUIZ: implement literal negation ===
    raise NotImplementedError("QUIZ: negate needs implementation")


class KB:
    def __init__(self, facts=None, rules=None):
        self.facts: Set[Expr] = set(facts or [])
        self.rules: List[Rule] = list(rules or [])

    def add_fact(self, fact):
        # === QUIZ: enforce literal integrity before adding ===
        raise NotImplementedError("QUIZ: add_fact needs implementation")

    def rule_modus_ponens(self) -> List[Expr]:
        # === QUIZ: derive new facts using modus ponens ===
        raise NotImplementedError("QUIZ: rule_modus_ponens needs implementation")

    def forward_chain(self, max_steps=1000, verbose=False):
        # === QUIZ: drive forward chaining using inference rules ===
        raise NotImplementedError("QUIZ: forward_chain needs implementation")