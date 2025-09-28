from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

# Allow importing the predicate reasoner from the previous stage.
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
        missing = [slot for slot in self.required_slots if slot not in slots]
        if missing:
            raise KeyError(f"Missing slots for template {self.name}: {missing}")
        method = getattr(self, "_render")
        return method(slots)


class TemplateEngine:
    def __init__(self) -> None:
        self._templates = {
            "parent_fact": ParentFactTemplate(),
            "parent_rule": ParentRuleTemplate(),
            "ancestor_transitivity": AncestorTransitivityTemplate(),
            "ancestor_query": AncestorQueryTemplate(),
        }

    def render(self, name: str, **slots: str) -> Predicate | Tuple:
        template = self._templates.get(name)
        if template is None:
            raise KeyError(f"Unknown template: {name}")
        return template.render({k: v for k, v in slots.items()})

    def available(self) -> Iterable[str]:
        return self._templates.keys()


@dataclass
class ParentFactTemplate(Template):
    name: str = "parent_fact"
    description: str = "Ground fact: X is a parent of Y"
    required_slots: Tuple[str, ...] = ("parent", "child")

    def _render(self, slots: Dict[str, str]) -> Predicate:
        return (
            "parent",
            slots["parent"].lower(),
            slots["child"].lower(),
        )


@dataclass
class ParentRuleTemplate(Template):
    name: str = "parent_rule"
    description: str = "Universal rule: every parent of someone is an ancestor"
    required_slots: Tuple[str, ...] = ()

    def _render(self, _slots: Dict[str, str]) -> Tuple:
        return (
            "FORALL",
            ("?x", "?y"),
            (
                "IMPLIES",
                (("parent", "?x", "?y"),),
                ("ancestor", "?x", "?y"),
            ),
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
        return (
            "FORALL",
            ("?x", "?y", "?z"),
            (
                "IMPLIES",
                (
                    ("parent", "?x", "?y"),
                    ("ancestor", "?y", "?z"),
                ),
                ("ancestor", "?x", "?z"),
            ),
        )


@dataclass
class AncestorQueryTemplate(Template):
    name: str = "ancestor_query"
    description: str = "Query ancestor relationships for a given target"
    required_slots: Tuple[str, ...] = ("target",)

    def _render(self, slots: Dict[str, str]) -> Predicate:
        return ("ancestor", "?who", slots["target"].lower())


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
    engine = TemplateEngine()
    kb = KB()
    examples = [
        DemoExample(
            text="Alice is a parent of Bob.",
            template="parent_fact",
            slots={"parent": "Alice", "child": "Bob"},
            expected=("parent", "alice", "bob"),
            check_note=(
                "Fact template lowers names and orders arguments correctly."
            ),
        ),
        DemoExample(
            text="Bob is a parent of Carol.",
            template="parent_fact",
            slots={"parent": "Bob", "child": "Carol"},
            expected=("parent", "bob", "carol"),
            check_note="Second fact mirrors the first with new constants.",
        ),
        DemoExample(
            text="Every parent is an ancestor of the person they parent.",
            template="parent_rule",
            slots={},
            expected=(
                "FORALL",
                ("?x", "?y"),
                (
                    "IMPLIES",
                    (("parent", "?x", "?y"),),
                    ("ancestor", "?x", "?y"),
                ),
            ),
            check_note="Universal template introduces ancestor rule.",
        ),
        DemoExample(
            text="Ancestor relationships are transitive via parentage.",
            template="ancestor_transitivity",
            slots={},
            expected=(
                "FORALL",
                ("?x", "?y", "?z"),
                (
                    "IMPLIES",
                    (
                        ("parent", "?x", "?y"),
                        ("ancestor", "?y", "?z"),
                    ),
                    ("ancestor", "?x", "?z"),
                ),
            ),
            check_note=(
                "Transitivity template combines parent and ancestor facts."
            ),
        ),
    ]

    results: List[DemoResult] = []
    for example in examples:
        logic = engine.render(example.template, **example.slots)
        valid = logic == example.expected
        results.append(
            DemoResult(
                example.text,
                logic,
                valid,
                example.check_note,
            )
        )
        if example.include_in_kb:
            if isinstance(logic, tuple) and logic and logic[0] == "FORALL":
                kb.add_rule(logic)
            else:
                kb.add_fact(logic)  # type: ignore[arg-type]

    kb.forward_chain()
    query_logic = engine.render("ancestor_query", target="carol")
    answers = kb.query(query_logic)  # type: ignore[arg-type]
    success = any(answer.get("?who") == "alice" for answer in answers)
    results.append(
        DemoResult(
            text="Who is an ancestor of Carol?",
            logic=query_logic,
            valid=success,
            note="Query succeeds after templates populate the KB.",
        )
    )
    return results, kb


__all__ = [
    "TemplateEngine",
    "run_demo",
    "DemoResult",
]