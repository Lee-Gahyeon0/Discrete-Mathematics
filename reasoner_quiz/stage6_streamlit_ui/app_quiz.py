from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "stage4_predicate"))

from reasoner import KB  # type: ignore

Fact = Tuple[str, ...]
Rule = Tuple

DEFAULT_FACTS = """parent(alice,bob)
parent(bob,carol)
parent(carol,dana)"""

DEFAULT_RULES = """forall x,y: parent(x,y) -> ancestor(x,y)
forall x,y,z: parent(x,y) & ancestor(y,z) -> ancestor(x,z)
forall x,y: ancestor(x,y) -> connected(x,y)"""

DEFAULT_QUERY = "ancestor(?who, dana)"


class ParseError(Exception):
    """Raised when the text-based KB format cannot be parsed."""


def parse_fact(line: str) -> Fact:
    # === QUIZ: parse a textual fact into predicate tuple ===
    raise NotImplementedError("QUIZ: parse_fact needs implementation")


def parse_predicate(token: str, variables: Sequence[str]) -> Fact:
    # === QUIZ: parse predicate tokens, normalizing variables and constants ===
    raise NotImplementedError("QUIZ: parse_predicate needs implementation")


def parse_rule(line: str) -> Rule:
    # === QUIZ: translate surface rule syntax into Stage 4 format ===
    raise NotImplementedError("QUIZ: parse_rule needs implementation")


def parse_facts_block(text: str) -> List[Fact]:
    # === QUIZ: split multi-line facts and parse each line ===
    raise NotImplementedError("QUIZ: parse_facts_block needs implementation")


def parse_rules_block(text: str) -> List[Rule]:
    # === QUIZ: parse a block of rule lines ===
    raise NotImplementedError("QUIZ: parse_rules_block needs implementation")


def parse_query(text: str) -> Fact:
    # === QUIZ: parse a query string into predicate form ===
    raise NotImplementedError("QUIZ: parse_query needs implementation")


def main() -> None:
    # === QUIZ: build Streamlit UI that wires parsing to the KB ===
    raise NotImplementedError("QUIZ: main needs implementation")


if __name__ == "__main__":
    main()
