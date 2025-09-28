from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)


Term = object
Predicate = Tuple[str, ...]
Substitution = Dict[str, Term]


def is_variable(term: Term) -> bool:
    return isinstance(term, str) and term.startswith("?")


def substitute(expr: Term, subs: Substitution) -> Term:
    if isinstance(expr, str):
        return subs.get(expr, expr)
    if isinstance(expr, tuple):
        return tuple(substitute(part, subs) for part in expr)
    return expr


def occurs_check(var: str, value: Term, subs: Substitution) -> bool:
    if var == value:
        return True
    if isinstance(value, str) and is_variable(value) and value in subs:
        return occurs_check(var, subs[value], subs)
    if isinstance(value, tuple):
        return any(occurs_check(var, part, subs) for part in value)
    return False


def unify(x: Term, y: Term, subs: Optional[Substitution] = None) -> Optional[Substitution]:
    if subs is None:
        subs = {}
    if x == y:
        return subs
    if isinstance(x, str) and is_variable(x):
        return unify_var(x, y, subs)
    if isinstance(y, str) and is_variable(y):
        return unify_var(y, x, subs)
    if isinstance(x, tuple) and isinstance(y, tuple) and len(x) == len(y):
        for left, right in zip(x, y):
            subs = unify(left, right, subs)
            if subs is None:
                return None
        return subs
    return None


def unify_var(var: str, value: Term, subs: Substitution) -> Optional[Substitution]:
    if var in subs:
        return unify(subs[var], value, subs)
    if isinstance(value, str) and value in subs and is_variable(value):
        return unify(var, subs[value], subs)
    if occurs_check(var, value, subs):
        return None
    subs[var] = value
    return subs


def is_ground(fact: Predicate) -> bool:
    return all(not (isinstance(arg, str) and is_variable(arg)) for arg in fact)


def is_exists(expr: Term) -> bool:
    return isinstance(expr, tuple) and len(expr) == 3 and expr[0] == "EXISTS"


@dataclass
class Rule:
    variables: Tuple[str, ...]
    premises: Tuple[Predicate, ...]
    conclusion: Term


class KB:
    def __init__(
        self,
        facts: Optional[Iterable[Predicate]] = None,
        rules: Optional[Iterable[Term]] = None,
    ) -> None:
        self.facts: Set[Predicate] = set()
        self.rules: List[Rule] = []
        self._exist_counter = 0
        for fact in facts or []:
            self.add_fact(fact)
        for rule in rules or []:
            self.add_rule(rule)

    def add_fact(self, fact: Predicate) -> bool:
        if not isinstance(fact, tuple) or not fact:
            raise ValueError("Facts must be predicate tuples")
        if not is_ground(fact):
            raise ValueError("Facts must be ground (no free variables)")
        if fact in self.facts:
            return False
        self.facts.add(fact)
        return True

    def add_rule(self, rule: Term) -> None:
        if isinstance(rule, Rule):
            self.rules.append(rule)
            return
        parsed = self._parse_rule(rule)
        self.rules.append(parsed)

    def forward_chain(self, max_iterations: int = 50) -> None:
        for _ in range(max_iterations):
            new_facts: List[Predicate] = []
            for rule in self.rules:
                for theta in self._satisfying_substitutions(rule.premises):
                    conclusion = substitute(rule.conclusion, theta)
                    if is_exists(conclusion):
                        fact = self._instantiate_exists(conclusion)
                    else:
                        fact = conclusion
                    if not isinstance(fact, tuple):
                        continue
                    if not is_ground(fact):
                        continue
                    if self.add_fact(fact):
                        new_facts.append(fact)
            if not new_facts:
                break

    def query(self, pattern: Predicate) -> List[Substitution]:
        answers: List[Substitution] = []
        for fact in self.facts:
            theta = unify(pattern, fact, {})
            if theta is not None:
                answers.append(theta)
        return answers

    def _satisfying_substitutions(self, premises: Sequence[Predicate]) -> Iterator[Substitution]:
        def backtrack(idx: int, current: Substitution) -> Iterator[Substitution]:
            if idx == len(premises):
                yield dict(current)
                return
            goal = substitute(premises[idx], current)
            for fact in self.facts:
                theta = unify(goal, fact, dict(current))
                if theta is not None:
                    yield from backtrack(idx + 1, theta)

        return backtrack(0, {})

    def _instantiate_exists(self, expr: Term) -> Predicate:
        _, variables, body = expr
        if not isinstance(variables, (list, tuple)):
            raise ValueError("Existential quantifier expects iterable of variables")
        subs: Substitution = {}
        for var in variables:
            if not isinstance(var, str) or not is_variable(var):
                raise ValueError(
                    "Existential variables must be strings starting with ?"
                )
            self._exist_counter += 1
            subs[var] = f"_sk{self._exist_counter}"
        return substitute(body, subs)  # type: ignore[return-value]

    def _parse_rule(self, expr: Term) -> Rule:
        if not (
            isinstance(expr, tuple)
            and len(expr) == 3
            and expr[0] == "FORALL"
        ):
            raise ValueError(
                "Rules must be encoded as ('FORALL', vars, "
                "('IMPLIES', premises, conclusion))"
            )
        vars_part, implies_part = expr[1], expr[2]
        if not isinstance(vars_part, (list, tuple)):
            raise ValueError("Quantified variables must be a list or tuple")
        variables = tuple(str(var) for var in vars_part)
        if not (
            isinstance(implies_part, tuple)
            and len(implies_part) == 3
            and implies_part[0] == "IMPLIES"
        ):
            raise ValueError("Body must be an IMPLIES tuple")
        raw_premises, conclusion = implies_part[1], implies_part[2]
        premises = self._normalize_premises(raw_premises)
        return Rule(variables, premises, conclusion)

    def _normalize_premises(self, raw: Term) -> Tuple[Predicate, ...]:
        if raw is None:
            return tuple()
        if isinstance(raw, tuple) and raw and raw[0] == "AND":
            parts = raw[1:]
        elif isinstance(raw, (list, tuple)) and raw and isinstance(raw[0], tuple):
            parts = raw
        else:
            parts = (raw,)
        normalized: List[Predicate] = []
        for part in parts:
            if not (isinstance(part, tuple) and part):
                raise ValueError("Premises must be predicate tuples")
            normalized.append(part)
        return tuple(normalized)


__all__ = ["KB", "Rule", "unify", "substitute", "is_variable"]