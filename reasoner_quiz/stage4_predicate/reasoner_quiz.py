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
    # === QUIZ: implement recursive unification ===
    raise NotImplementedError("QUIZ: unify needs implementation")


def unify_var(var: str, value: Term, subs: Substitution) -> Optional[Substitution]:
    # === QUIZ: handle variable binding during unification ===
    raise NotImplementedError("QUIZ: unify_var needs implementation")


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

    def add_fact(self, fact: Predicate) -> bool:
        if fact in self.facts:
            return False
        self.facts.add(fact)
        return True

    def add_rule(self, rule: Term) -> None:
        parsed = rule if isinstance(rule, Rule) else self._parse_rule(rule)
        self.rules.append(parsed)

    def forward_chain(self, max_iterations: int = 50) -> None:
        # === QUIZ: repeatedly apply rules and grow the fact set ===
        raise NotImplementedError("QUIZ: forward_chain needs implementation")

    def query(self, pattern: Predicate) -> List[Substitution]:
        # === QUIZ: perform pattern matching against known facts ===
        raise NotImplementedError("QUIZ: query needs implementation")

    def _satisfying_substitutions(self, premises: Sequence[Predicate]) -> Iterator[Substitution]:
        # === QUIZ: backtracking search for substitutions that satisfy premises ===
        raise NotImplementedError("QUIZ: _satisfying_substitutions needs implementation")

    def _instantiate_exists(self, expr: Term) -> Predicate:
        # === QUIZ: skolemize existential quantifiers ===
        raise NotImplementedError("QUIZ: _instantiate_exists needs implementation")

    def _parse_rule(self, expr: Term) -> Rule:
        # === QUIZ: convert a FORALL/IMPLIES expression into a Rule dataclass ===
        raise NotImplementedError("QUIZ: _parse_rule needs implementation")

    def _normalize_premises(self, raw: Term) -> Tuple[Predicate, ...]:
        # === QUIZ: normalize raw premises into a tuple of predicates ===
        raise NotImplementedError("QUIZ: _normalize_premises needs implementation")


__all__ = ["KB", "Rule", "unify", "substitute", "is_variable"]
