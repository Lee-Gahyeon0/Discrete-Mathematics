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
    return literal[1] if is_not(literal) else ("NOT", literal)


class KB:
    def __init__(self, facts=None, rules=None):
        self.facts: Set[Expr] = set(facts or [])
        self.rules: List[Rule] = list(rules or [])
        for fact in list(self.facts):
            if is_lit(fact) and negate(fact) in self.facts:
                raise ValueError("Contradiction detected")

    def add_fact(self, fact):
        if not is_lit(fact):
            raise ValueError
        if fact in self.facts:
            return False
        if negate(fact) in self.facts:
            raise ValueError("Contradiction detected")
        self.facts.add(fact)
        return True

    def rule_modus_ponens(self) -> List[Expr]:
        new = []
        for tag, antecedent, consequent in self.rules:
            if tag != "IMPLIES":
                continue
            if antecedent in self.facts and consequent not in self.facts:
                new.append(consequent)
        return new

    def forward_chain(self, max_steps=1000, verbose=False):
        for _ in range(max_steps):
            added = False
            for fact in self.rule_modus_ponens():
                if self.add_fact(fact):
                    added = True
            if not added:
                break