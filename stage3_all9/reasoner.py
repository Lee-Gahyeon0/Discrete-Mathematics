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
        for fact in list(self.facts):
            if is_lit(fact) and negate(fact) in self.facts:
                raise ValueError("Contradiction detected")

    def add_fact(self, fact):
        if fact in self.facts:
            return False
        if is_lit(fact) and negate(fact) in self.facts:
            raise ValueError("Contradiction detected")
        self.facts.add(fact)
        return True

    def rule_modus_ponens(self) -> List[Expr]:
        out = []
        for rule in self.rules:
            if not is_implies(rule):
                continue
            antecedent, consequent = rule[1], rule[2]
            if (
                antecedent in self.facts
                and is_lit(consequent)
                and consequent not in self.facts
            ):
                out.append(consequent)
        return out

    def rule_modus_tollens(self) -> List[Expr]:
        out = []
        for rule in self.rules:
            if not is_implies(rule):
                continue
            antecedent, consequent = rule[1], rule[2]
            if (
                is_lit(antecedent)
                and is_lit(consequent)
                and negate(consequent) in self.facts
            ):
                negated = negate(antecedent)
                if negated not in self.facts:
                    out.append(negated)
        return out

    def rule_simplification(self) -> List[Expr]:
        out = []
        for fact in self.facts:
            if not is_and(fact):
                continue
            left, right = fact[1], fact[2]
            if is_lit(left) and left not in self.facts:
                out.append(left)
            if is_lit(right) and right not in self.facts:
                out.append(right)
        return out

    def rule_conjunction(self) -> List[Expr]:
        literals = [fact for fact in self.facts if is_lit(fact)]
        out = []
        count = len(literals)
        for i in range(count):
            for j in range(i + 1, count):
                candidate = ("AND", literals[i], literals[j])
                if candidate not in self.facts:
                    out.append(candidate)
        return out

    def rule_disjunctive_addition(self) -> List[Expr]:
        literals = [fact for fact in self.facts if is_lit(fact)]
        out = []
        for left in literals:
            for right in literals:
                if left == right:
                    continue
                disjunction = ("OR", left, right)
                if disjunction not in self.facts:
                    out.append(disjunction)
        return out

    def rule_disjunctive_syllogism(self) -> List[Expr]:
        out = []
        for fact in self.facts:
            if not is_or(fact):
                continue
            left, right = fact[1], fact[2]
            if is_lit(left) and is_lit(right):
                if negate(left) in self.facts and right not in self.facts:
                    out.append(right)
                if negate(right) in self.facts and left not in self.facts:
                    out.append(left)
        return out

    def rule_hypothetical_syllogism(self) -> List[Rule]:
        out = []
        implications = [rule for rule in self.rules if is_implies(rule)]
        for index, first in enumerate(implications):
            antecedent, middle = first[1], first[2]
            for j, second in enumerate(implications):
                if index == j:
                    continue
                next_antecedent, consequent = second[1], second[2]
                if middle == next_antecedent:
                    candidate = ("IMPLIES", antecedent, consequent)
                    if candidate not in self.rules and candidate not in out:
                        out.append(candidate)
        return out

    def rule_constructive_dilemma(self) -> List[Expr]:
        out = []
        implications = [rule for rule in self.rules if is_implies(rule)]
        disjunctions = [fact for fact in self.facts if is_or(fact)]
        for first in implications:
            antecedent_p, consequent_r = first[1], first[2]
            for second in implications:
                antecedent_q, consequent_s = second[1], second[2]
                for disjunction in disjunctions:
                    left, right = disjunction[1], disjunction[2]
                    if (
                        (left == antecedent_p and right == antecedent_q)
                        or (left == antecedent_q and right == antecedent_p)
                    ):
                        candidate = ("OR", consequent_r, consequent_s)
                        if candidate not in self.facts:
                            out.append(candidate)
        return out

    def rule_destructive_dilemma(self) -> List[Expr]:
        out = []
        implications = [rule for rule in self.rules if is_implies(rule)]
        disjunctions = [fact for fact in self.facts if is_or(fact)]
        for first in implications:
            antecedent_p, consequent_r = first[1], first[2]
            for second in implications:
                antecedent_q, consequent_s = second[1], second[2]
                for disjunction in disjunctions:
                    left, right = disjunction[1], disjunction[2]
                    if is_not(left) and is_not(right):
                        negated_set = {left[1], right[1]}
                        if (
                            consequent_r in negated_set
                            and consequent_s in negated_set
                            and consequent_r != consequent_s
                        ):
                            candidate = (
                                "OR",
                                negate(antecedent_p),
                                negate(antecedent_q),
                            )
                            if candidate not in self.facts:
                                out.append(candidate)
        return out

    def forward_chain(self, max_steps=1000, verbose=False):
        for _ in range(max_steps):
            changed = False
            for rule in self.rule_hypothetical_syllogism():
                self.rules.append(rule)
                changed = True
            inference_functions = [
                self.rule_modus_ponens,
                self.rule_modus_tollens,
                self.rule_simplification,
                self.rule_conjunction,
                self.rule_disjunctive_addition,
                self.rule_disjunctive_syllogism,
                self.rule_constructive_dilemma,
                self.rule_destructive_dilemma,
            ]
            for infer in inference_functions:
                for fact in infer():
                    try:
                        if self.add_fact(fact):
                            changed = True
                    except ValueError:
                        pass
            if not changed:
                break