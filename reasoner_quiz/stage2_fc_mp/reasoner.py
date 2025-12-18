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
    if is_atom(literal):
        return ("NOT", literal)
    elif is_not(literal):
        return literal[1]
    else:
        return ("NOT", literal)


class KB:
    def __init__(self, facts=None, rules=None):
        self.facts: Set[Expr] = set(facts or [])
        self.rules: List[Rule] = list(rules or [])

    def add_fact(self, fact):
        # === QUIZ: enforce literal integrity before adding ===
        if not is_lit(fact):
            return False

            # 모순 감지
        if negate(fact) in self.facts:
            raise ValueError(f"Contradiction detected: {fact} and {negate(fact)}")

        if fact in self.facts:
            return False

        self.facts.add(fact)
        return True

    def rule_modus_ponens(self) -> List[Expr]:
        # === QUIZ: derive new facts using modus ponens ===
        derived_facts = []
        for rule in self.rules:
            # 규칙 형식이 올바른지 확인
            if isinstance(rule, tuple) and len(rule) == 3 and rule[0] == 'IMPLIES':
                _, p, q = rule

                # 전제(P)가 사실에 있고, 결론(Q)가 아직 사실에 없다면 -> Q 도출
                if p in self.facts:
                    if q not in self.facts:
                        derived_facts.append(q)

        return derived_facts

    def forward_chain(self, max_steps=1000, verbose=False):
        # === QUIZ: drive forward chaining using inference rules ===
        step = 0
        while step < max_steps:
            # 1. 이번 단계에서 도출된 새로운 사실들 수집
            new_facts = self.rule_modus_ponens()

            # 2. 새로운 사실이 없으면 종료 (Fixpoint 도달)
            if not new_facts:
                break

            # 3. 새로운 사실을 KB에 추가 (여기서 모순 발생시 add_fact가 에러 발생시킴)
            added_count = 0
            for fact in new_facts:
                if self.add_fact(fact):
                    added_count += 1

            # 추가된 사실이 하나도 없으면(모두 중복이었다면) 종료
            if added_count == 0:
                break

            step += 1

        return self.facts