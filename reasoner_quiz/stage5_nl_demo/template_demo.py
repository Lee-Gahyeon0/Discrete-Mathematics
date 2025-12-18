from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "stage4_predicate"))

from reasoner import KB  # type: ignore

Predicate = Tuple[str, ...]


@dataclass
class Template:
    name: str
    description: str
    required_slots: Tuple[str, ...]

    def render(self, slots: Dict[str, str]) -> Predicate | Tuple:
        # === QUIZ: fill in template rendering with slot validation ===
        # 1. 필수 슬롯 검증 (KeyError 발생 확인)
        for req in self.required_slots:
            if req not in slots:
                raise KeyError(f"Missing required slot '{req}' for template '{self.name}'")

        # 2. 하위 클래스의 실제 렌더링 메서드 호출
        # (dataclass 구조상 _render는 하위 클래스에 정의됨)
        if hasattr(self, "_render"):
            return self._render(slots)
        raise NotImplementedError("Template subclass must implement _render method")


class TemplateEngine:
    def __init__(self) -> None:
        self._templates = {
            "parent_fact": ParentFactTemplate(),
            "parent_rule": ParentRuleTemplate(),
            "ancestor_transitivity": AncestorTransitivityTemplate(),
            "ancestor_query": AncestorQueryTemplate(),
        }

    def render(self, name: str, **slots: str) -> Predicate | Tuple:
        # === QUIZ: retrieve a template and render it with provided slots ===
        if name not in self._templates:
            raise ValueError(f"Unknown template: {name}")

        template = self._templates[name]
        return template.render(slots)

    def available(self) -> Iterable[str]:
        return self._templates.keys()


    def available(self) -> Iterable[str]:
        return self._templates.keys()


@dataclass
class ParentFactTemplate(Template):
    name: str = "parent_fact"
    description: str = "Ground fact: X is a parent of Y"
    required_slots: Tuple[str, ...] = ("parent", "child")

    def _render(self, slots: Dict[str, str]) -> Predicate:
        # === QUIZ: build parent fact predicate from slots ===
        # 대문자 입력 -> 소문자 정규화 (Alice -> alice)
        p = slots["parent"].lower()
        c = slots["child"].lower()
        return ("parent", p, c)

@dataclass
class ParentRuleTemplate(Template):
    name: str = "parent_rule"
    description: str = "Universal rule: every parent of someone is an ancestor"
    required_slots: Tuple[str, ...] = ()

    def _render(self, _slots: Dict[str, str]) -> Tuple:
        # === QUIZ: produce the FORALL implication for parent -> ancestor ===
        # Forall x, y: parent(x, y) -> ancestor(x, y)
        return (
            "FORALL",
            ["?x", "?y"],
            ("IMPLIES", ("parent", "?x", "?y"), ("ancestor", "?x", "?y")),
        )

@dataclass
class AncestorTransitivityTemplate(Template):
    name: str = "ancestor_transitivity"
    description: str = (
        "If someone is a parent of a person who is an ancestor, they are also "
        "an ancestor"
    )
    required_slots: Tuple[str, ...] = ()

    def _render(self, _slots: Dict[str, str]) -> Tuple:
        # === QUIZ: produce the FORALL implication encoding transitivity ===
        # Forall x, y, z: parent(x, y) AND ancestor(y, z) -> ancestor(x, z)
        return (
            "FORALL",
            ["?x", "?y", "?z"],
            (
                "IMPLIES",
                [("parent", "?x", "?y"), ("ancestor", "?y", "?z")],
                ("ancestor", "?x", "?z"),
            ),
        )


@dataclass
class AncestorQueryTemplate(Template):
    name: str = "ancestor_query"
    description: str = "Query ancestor relationships for a given target"
    required_slots: Tuple[str, ...] = ("target",)

    def _render(self, slots: Dict[str, str]) -> Predicate:
        # === QUIZ: create query predicate targeting a specific individual ===
        # 특정 대상(target)의 조상이 누구인지 묻는 질의 패턴을 생성
        target = slots["target"].lower()
        return ("ancestor", "?who", target)

@dataclass
class DemoExample:
    text: str
    template: str
    slots: Dict[str, str]
    expected: Predicate | Tuple
    include_in_kb: bool = True
    check_note: str = ""


@dataclass
class DemoResult:
    text: str
    logic: Predicate | Tuple
    valid: bool
    note: str


def run_demo() -> Tuple[List[DemoResult], KB]:
    # === QUIZ: wire templates, populate KB, and execute query ===
    engine = TemplateEngine()
    kb = KB()
    demo_results = []

    # 1. 시나리오 정의
    # Alice -> Bob -> Carol 관계 설정 및 추론 규칙 정의
    examples = [
        DemoExample(
            text="Alice is a parent of Bob",
            template="parent_fact",
            slots={"parent": "Alice", "child": "Bob"},
            expected=("parent", "alice", "bob"),
            check_note="Fact added"
        ),
        DemoExample(
            text="Bob is a parent of Carol",
            template="parent_fact",
            slots={"parent": "Bob", "child": "Carol"},
            expected=("parent", "bob", "carol"),
            check_note="Fact added"
        ),
        DemoExample(
            text="Rule: Parent implies Ancestor",
            template="parent_rule",
            slots={},
            expected=("FORALL", ["?x", "?y"], ("IMPLIES", ("parent", "?x", "?y"), ("ancestor", "?x", "?y"))),
            check_note="Rule added"
        ),
        DemoExample(
            text="Rule: Ancestor Transitivity",
            template="ancestor_transitivity",
            slots={},
            expected=("FORALL", ["?x", "?y", "?z"],
                      ("IMPLIES", [("parent", "?x", "?y"), ("ancestor", "?y", "?z")], ("ancestor", "?x", "?z"))),
            check_note="Rule added"
        )
    ]

    # 2. 템플릿 렌더링 및 KB 주입
    for ex in examples:
        logic_output = engine.render(ex.template, **ex.slots)

        # KB에 추가 (튜플의 첫 요소가 FORALL이면 규칙, 아니면 사실로 간주)
        if ex.include_in_kb:
            if logic_output[0] == "FORALL":
                kb.add_rule(logic_output)
            else:
                kb.add_fact(logic_output)  # type: ignore

        demo_results.append(
            DemoResult(
                text=ex.text,
                logic=logic_output,
                valid=(logic_output == ex.expected),
                note=ex.check_note
            )
        )

    # 3. 추론 실행 (Forward Chaining)
    kb.forward_chain()

    # 4. 질의 실행: Carol의 조상은 누구인가?
    query_text = "Who is an ancestor of Carol?"
    query_logic = engine.render("ancestor_query", target="Carol")
    substitutions = kb.query(query_logic)  # type: ignore

    # 5. 결과 검증 (Alice가 결과에 포함되어야 함)
    found_ancestors = [s.get("?who") for s in substitutions]
    is_success = "alice" in found_ancestors

    demo_results.append(
        DemoResult(
            text=query_text,
            logic=query_logic,
            valid=is_success,
            note=f"Found ancestors: {found_ancestors}"
        )
    )

    return demo_results, kb


__all__ = [
    "TemplateEngine",
    "run_demo",
    "DemoResult",
]
