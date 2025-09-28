from typing import List, Set, Tuple, Union

Expr = Union[str, Tuple]
Rule = Tuple[str, Expr, Expr]


def is_atom(value):
    return isinstance(value, str)


def is_not(value):
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and value[0] == "NOT"
        and is_atom(value[1])
    )


def is_lit(value):
    return is_atom(value) or is_not(value)


def is_and(value):
    return isinstance(value, tuple) and len(value) == 3 and value[0] == "AND"


def is_or(value):
    return isinstance(value, tuple) and len(value) == 3 and value[0] == "OR"


def is_implies(value):
    return isinstance(value, tuple) and len(value) == 3 and value[0] == "IMPLIES"


def negate(literal):
    return literal[1] if is_not(literal) else ("NOT", literal)


class KB:
    def __init__(self, facts=None, rules=None):
        self.facts: Set[Expr] = set(facts or [])
        self.rules: List[Rule] = list(rules or [])

    def add_fact(self, fact):
        if fact in self.facts:
            return False
        self.facts.add(fact)
        return True

    def rule_modus_ponens(self) -> List[Expr]:
        # === QUIZ: implement modus ponens inference ===
        raise NotImplementedError("QUIZ: rule_modus_ponens needs implementation")

    def rule_modus_tollens(self) -> List[Expr]:
        # === QUIZ: implement modus tollens inference ===
        raise NotImplementedError("QUIZ: rule_modus_tollens needs implementation")

    def rule_simplification(self) -> List[Expr]:
        # === QUIZ: split conjunction facts into literals ===
        raise NotImplementedError("QUIZ: rule_simplification needs implementation")

    def rule_conjunction(self) -> List[Expr]:
        # === QUIZ: combine literals into conjunctions ===
        raise NotImplementedError("QUIZ: rule_conjunction needs implementation")

    def rule_disjunctive_addition(self) -> List[Expr]:
        # === QUIZ: create disjunctions from literals ===
        raise NotImplementedError("QUIZ: rule_disjunctive_addition needs implementation")

    def rule_disjunctive_syllogism(self) -> List[Expr]:
        # === QUIZ: drop negated disjuncts to infer the other ===
        raise NotImplementedError("QUIZ: rule_disjunctive_syllogism needs implementation")

    def rule_hypothetical_syllogism(self) -> List[Rule]:
        # === QUIZ: chain implications to form new rules ===
        raise NotImplementedError("QUIZ: rule_hypothetical_syllogism needs implementation")

    def rule_constructive_dilemma(self) -> List[Expr]:
        # === QUIZ: implement constructive dilemma ===
        raise NotImplementedError("QUIZ: rule_constructive_dilemma needs implementation")

    def rule_destructive_dilemma(self) -> List[Expr]:
        # === QUIZ: implement destructive dilemma ===
        raise NotImplementedError("QUIZ: rule_destructive_dilemma needs implementation")

    def forward_chain(self, max_steps=1000, verbose=False):
        # === QUIZ: orchestrate repeated inference applications ===
        raise NotImplementedError("QUIZ: forward_chain needs implementation")