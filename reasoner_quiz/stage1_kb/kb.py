from typing import Set, Tuple, Union

Expr = Union[str, Tuple[str, str]]


def is_atom(value):
    return isinstance(value, str)


def is_not(value):
    # === QUIZ: implement NOT predicate detection ===
    return isinstance(value, tuple) and len(value) == 2 and value[0] == 'NOT'


def is_lit(value):
    # === QUIZ: determine if a value is a literal (atom or NOT(atom)) ===
    return is_atom(value) or is_not(value)


def negate(literal):
    # === QUIZ: return the logical negation of a literal ===
    if is_atom(literal):
        return ("NOT", literal)
    elif is_not(literal):
        return literal[1]
    else:
        # 리터럴이 아닌 경우 강제로 부정 래핑 (혹시나)
        return ("NOT", literal)


class KB:
    def __init__(self):
        self.facts: Set[Expr] = set()

    def add_fact(self, fact: Expr) -> bool:
        # === QUIZ: validate and insert a literal fact into the KB ===
        # 1. 타입 검사
        if not is_lit(fact):
            return False

        # 2. 모순 검사 (Contradiction Check)
        # 예: "P"를 넣으려는데 이미 ("NOT", "P")가 있으면 에러
        negated_fact = negate(fact)
        if negated_fact in self.facts:
            raise ValueError(f"Contradiction detected: {fact} and {negated_fact}")

        # 3. 중복 검사 (Duplicate Check)
        if fact in self.facts:
            return False

        # 4. 사실 추가
        self.facts.add(fact)
        return True
