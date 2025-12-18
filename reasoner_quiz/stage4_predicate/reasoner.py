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
    if subs is None:
        subs = {}

    term_a = substitute(x, subs)
    term_b = substitute(y, subs)

    if term_a == term_b:
        return subs

    if is_variable(term_a):
        return unify_var(term_a, term_b, subs)

    if is_variable(term_b):
        return unify_var(term_b, term_a, subs)

    if isinstance(term_a, tuple) and isinstance(term_b, tuple):
        if len(term_a) != len(term_b):
            return None

        current_bindings = subs
        for part_a, part_b in zip(term_a, term_b):
            current_bindings = unify(part_a, part_b, current_bindings)
            if current_bindings is None:
                return None
        return current_bindings

    return None


def unify_var(var: str, value: Term, subs: Substitution) -> Optional[Substitution]:
    # === QUIZ: handle variable binding during unification ===
    if var in subs:
        return unify(subs[var], value, subs)

    if isinstance(value, str) and is_variable(value) and value in subs:
        return unify(var, subs[value], subs)

    if occurs_check(var, value, subs):
        return None

    updated_subs = subs.copy()
    updated_subs[var] = value
    return updated_subs


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

        # 뼈대에는 없지만 초기화 로직이 필요하여 추가 (테스트 통과 필수)
        if facts:
            for f in facts:
                self.add_fact(f)
        if rules:
            for r in rules:
                self.add_rule(r)

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
        for _ in range(max_iterations):
            fact_added = False
            for rule in self.rules:
                for bindings in self._satisfying_substitutions(rule.premises):
                    conclusion_term = rule.conclusion

                    if is_exists(conclusion_term):
                        # 이미 스콜렘 상수로 치환된 결과가 존재하는지 확인 (무한 생성 방지)
                        check_pattern = substitute(conclusion_term[2], bindings)
                        if self.query(check_pattern):
                            continue

                        inferred_fact = self._instantiate_exists(substitute(conclusion_term, bindings))
                    else:
                        inferred_fact = substitute(conclusion_term, bindings)

                    if self.add_fact(inferred_fact):
                        fact_added = True

            if not fact_added:
                break

    def query(self, pattern: Predicate) -> List[Substitution]:
        # === QUIZ: perform pattern matching against known facts ===
        matched_results = []
        for known_fact in self.facts:
            match_subs = unify(pattern, known_fact)
            if match_subs is not None:
                matched_results.append(match_subs)
        return matched_results

    def _satisfying_substitutions(self, premises: Sequence[Predicate]) -> Iterator[Substitution]:
        # === QUIZ: backtracking search for substitutions that satisfy premises ===
        def dfs_search(idx: int, current_subs: Substitution) -> Iterator[Substitution]:
            if idx == len(premises):
                yield current_subs
                return

            target_premise = substitute(premises[idx], current_subs)

            # 런타임 중 집합 변경 방지를 위해 리스트로 복사 후 순회
            for fact in list(self.facts):
                next_subs = unify(target_premise, fact, current_subs.copy())
                if next_subs is not None:
                    yield from dfs_search(idx + 1, next_subs)

        return dfs_search(0, {})

    def _instantiate_exists(self, expr: Term) -> Predicate:
        # === QUIZ: skolemize existential quantifiers ===
        variables_to_skolemize = expr[1]
        if isinstance(variables_to_skolemize, str):
            variables_to_skolemize = [variables_to_skolemize]

        formula_body = expr[2]
        skolem_map = {}

        for var_name in variables_to_skolemize:
            unique_skolem = f"_sk{self._exist_counter}"
            self._exist_counter += 1
            skolem_map[var_name] = unique_skolem

        return substitute(formula_body, skolem_map)
    def _parse_rule(self, expr: Term) -> Rule:
        # === QUIZ: convert a FORALL/IMPLIES expression into a Rule dataclass ===
        if isinstance(expr, tuple) and expr[0] == "FORALL":
            variables = tuple(expr[1])
            body = expr[2]

            if isinstance(body, tuple) and body[0] == "IMPLIES":
                premises = self._normalize_premises(body[1])
                conclusion = body[2]
                return Rule(variables=variables, premises=premises, conclusion=conclusion)

            if isinstance(body, tuple) and len(body) == 2 and isinstance(body[0], list):
                premises = self._normalize_premises(body[0])
                conclusion = body[1]
                return Rule(variables=variables, premises=premises, conclusion=conclusion)

            raise ValueError(f"Invalid rule format: {expr}")

    def _normalize_premises(self, raw: Term) -> Tuple[Predicate, ...]:
        # === QUIZ: normalize raw premises into a tuple of predicates ===
        if isinstance(raw, list):
            return tuple(raw)
        if isinstance(raw, tuple) and raw[0] == "AND":
            return (raw[1], raw[2])
        return (raw,)

__all__ = ["KB", "Rule", "unify", "substitute", "is_variable"]
