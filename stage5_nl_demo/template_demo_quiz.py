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
        raise NotImplementedError("QUIZ: Template.render needs implementation")


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
        raise NotImplementedError("QUIZ: TemplateEngine.render needs implementation")

    def available(self) -> Iterable[str]:
        return self._templates.keys()


@dataclass
class ParentFactTemplate(Template):
    name: str = "parent_fact"
    description: str = "Ground fact: X is a parent of Y"
    required_slots: Tuple[str, ...] = ("parent", "child")

    def _render(self, slots: Dict[str, str]) -> Predicate:
        # === QUIZ: build parent fact predicate from slots ===
        raise NotImplementedError("QUIZ: ParentFactTemplate._render needs implementation")


@dataclass
class ParentRuleTemplate(Template):
    name: str = "parent_rule"
    description: str = "Universal rule: every parent of someone is an ancestor"
    required_slots: Tuple[str, ...] = ()

    def _render(self, _slots: Dict[str, str]) -> Tuple:
        # === QUIZ: produce the FORALL implication for parent -> ancestor ===
        raise NotImplementedError("QUIZ: ParentRuleTemplate._render needs implementation")


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
        raise NotImplementedError(
            "QUIZ: AncestorTransitivityTemplate._render needs implementation"
        )


@dataclass
class AncestorQueryTemplate(Template):
    name: str = "ancestor_query"
    description: str = "Query ancestor relationships for a given target"
    required_slots: Tuple[str, ...] = ("target",)

    def _render(self, slots: Dict[str, str]) -> Predicate:
        # === QUIZ: create query predicate targeting a specific individual ===
        raise NotImplementedError("QUIZ: AncestorQueryTemplate._render needs implementation")


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
    raise NotImplementedError("QUIZ: run_demo needs implementation")


__all__ = [
    "TemplateEngine",
    "run_demo",
    "DemoResult",
]