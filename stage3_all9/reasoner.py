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
        # P, P->Q => Q
        derived = []
        for rule in self.rules:
            if is_implies(rule):
                _, p, q = rule
                if p in self.facts and q not in self.facts:
                    derived.append(q)
        return derived

    def rule_modus_tollens(self) -> List[Expr]:
        # === QUIZ: implement modus tollens inference ===
        # not Q, P->Q => not P
        derived = []
        for rule in self.rules:
            if is_implies(rule):
                _, p, q = rule
                not_q = negate(q)
                if not_q in self.facts:
                    not_p = negate(p)
                    if not_p not in self.facts:
                        derived.append(not_p)
        return derived

    def rule_simplification(self) -> List[Expr]:
        # === QUIZ: split conjunction facts into literals ===
        # (P AND Q) => P, Q
        derived = []
        for fact in self.facts:
            if is_and(fact):
                _, p, q = fact
                if p not in self.facts: derived.append(p)
                if q not in self.facts: derived.append(q)
        return derived

    def rule_conjunction(self) -> List[Expr]:
        # === QUIZ: combine literals into conjunctions ===
        # P, Q => (P AND Q)
        derived = []
        for rule in self.rules:
            if is_implies(rule):
                ant = rule[1]
                if is_and(ant):
                    _, p, q = ant
                    if p in self.facts and q in self.facts:
                        if ant not in self.facts:
                            derived.append(ant)
        return derived

    def rule_disjunctive_addition(self) -> List[Expr]:
        # === QUIZ: create disjunctions from literals ===
        # P => (P OR Q) (목표 없으므로 빈 리스트)
        return []

    def rule_disjunctive_syllogism(self) -> List[Expr]:
        # === QUIZ: drop negated disjuncts to infer the other ===
        # (P OR Q), not P => Q
        derived = []
        for fact in self.facts:
            if is_or(fact):
                _, p, q = fact
                if negate(p) in self.facts and q not in self.facts:
                    derived.append(q)
                elif negate(q) in self.facts and p not in self.facts:
                    derived.append(p)
        return derived

    def rule_hypothetical_syllogism(self) -> List[Rule]:
        # === QUIZ: chain implications to form new rules ===
        # P->Q, Q->R => P->R
        new_rules = []
        for r1 in self.rules:
            if not is_implies(r1): continue
            for r2 in self.rules:
                if not is_implies(r2): continue
                if r1 == r2: continue

                if r1[2] == r2[1]:
                    new_rule = ("IMPLIES", r1[1], r2[2])
                    if new_rule not in self.rules and new_rule not in new_rules:
                        new_rules.append(new_rule)
        return new_rules

    def rule_constructive_dilemma(self) -> List[Expr]:
        # === QUIZ: implement constructive dilemma ===
        # (P OR R), P->Q, R->S => (Q OR S)
        derived = []
        for fact in self.facts:
            if is_or(fact):
                _, p, r = fact

                q = None
                for rule in self.rules:
                    if is_implies(rule) and rule[1] == p:
                        q = rule[2]
                        break

                s = None
                for rule in self.rules:
                    if is_implies(rule) and rule[1] == r:
                        s = rule[2]
                        break

                if q and s:
                    new_or = ("OR", q, s)
                    if new_or not in self.facts:
                        derived.append(new_or)
        return derived
    def rule_destructive_dilemma(self) -> List[Expr]:
        # === QUIZ: implement destructive dilemma ===
        # (not Q OR not S), P->Q, R->S => (not P OR not R)
        derived = []
        for fact in self.facts:
            if is_or(fact):
                _, nq, ns = fact

                p = None
                for rule in self.rules:
                    if is_implies(rule) and negate(rule[2]) == nq:
                        p = rule[1]
                        break

                r = None
                for rule in self.rules:
                    if is_implies(rule) and negate(rule[2]) == ns:
                        r = rule[1]
                        break

                if p and r:
                    new_val = ("OR", negate(p), negate(r))
                    if new_val not in self.facts:
                        derived.append(new_val)
        return derived

    def forward_chain(self, max_steps=1000, verbose=False):
        # === QUIZ: orchestrate repeated inference applications ===
        for _ in range(max_steps):
            new_facts = set()
            new_rules = []

            # 1. Facts
            new_facts.update(self.rule_modus_ponens())
            new_facts.update(self.rule_modus_tollens())
            new_facts.update(self.rule_simplification())
            new_facts.update(self.rule_conjunction())
            new_facts.update(self.rule_disjunctive_addition())
            new_facts.update(self.rule_disjunctive_syllogism())
            new_facts.update(self.rule_constructive_dilemma())
            new_facts.update(self.rule_destructive_dilemma())

            # 2. Rules
            generated_rules = self.rule_hypothetical_syllogism()
            for r in generated_rules:
                if r not in self.rules:
                    new_rules.append(r)

            # 3. Update
            changed = False
            for f in new_facts:
                if self.add_fact(f): changed = True
            for r in new_rules:
                if self.add_rule(r): changed = True

            if not changed:
                break

        return self.facts