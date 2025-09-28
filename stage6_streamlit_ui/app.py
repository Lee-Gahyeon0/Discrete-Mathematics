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
    match = re.fullmatch(
        r"\s*([A-Za-z_][A-Za-z0-9_]*)\(([^)]*)\)\s*",
        line,
    )
    if not match:
        raise ParseError(f"Could not parse fact: {line}")
    pred = match.group(1)
    args = [
        tok.strip().lower()
        for tok in match.group(2).split(",")
        if tok.strip()
    ]
    return tuple([pred] + args)


def parse_predicate(token: str, variables: Sequence[str]) -> Fact:
    match = re.fullmatch(
        r"\s*([A-Za-z_][A-Za-z0-9_]*)\(([^)]*)\)\s*",
        token,
    )
    if not match:
        raise ParseError(f"Could not parse predicate: {token}")
    pred = match.group(1)
    raw_args = [
        part.strip()
        for part in match.group(2).split(",")
        if part.strip()
    ]
    args: List[str] = []
    for arg in raw_args:
        if arg.startswith("?"):
            args.append(arg)
        elif arg in variables:
            args.append(f"?{arg}")
        else:
            args.append(arg.lower())
    return tuple([pred] + args)


def parse_rule(line: str) -> Rule:
    if not line.strip():
        raise ParseError("Rule line is empty")
    headless = line.strip()
    if not headless.lower().startswith("forall"):
        raise ParseError("Rules must start with 'forall'")
    try:
        quantifier, body = headless.split(":", 1)
    except ValueError as exc:
        raise ParseError(
            "Rule must contain ':' separating quantifier and body"
        ) from exc
    var_segment = quantifier[6:].strip()
    variables = [
        name.strip()
        for name in var_segment.split(",")
        if name.strip()
    ]
    if not variables:
        raise ParseError("Quantifier must list at least one variable")
    try:
        antecedent_text, consequent_text = body.split("->", 1)
    except ValueError as exc:
        raise ParseError(
            "Rule body must use '->' between premises and conclusion"
        ) from exc
    premise_tokens = [
        tok.strip()
        for tok in antecedent_text.split("&")
        if tok.strip()
    ]
    if not premise_tokens:
        raise ParseError("Rule must contain at least one premise")
    premises = tuple(parse_predicate(token, variables) for token in premise_tokens)
    conclusion = parse_predicate(consequent_text.strip(), variables)
    return (
        "FORALL",
        tuple(f"?{v}" for v in variables),
        ("IMPLIES", premises, conclusion),
    )


def parse_facts_block(text: str) -> List[Fact]:
    facts: List[Fact] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        facts.append(parse_fact(stripped))
    return facts


def parse_rules_block(text: str) -> List[Rule]:
    rules: List[Rule] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rules.append(parse_rule(stripped))
    return rules


def parse_query(text: str) -> Fact:
    return parse_predicate(text.strip(), ())


def main() -> None:
    st.set_page_config(page_title="Predicate Knowledge Base", layout="wide")
    st.title("Streamlit Knowledge-Base Playground")
    st.caption(
        "Edit facts and rules, then execute the Stage 4 predicate reasoner to "
        "see inferred results."
    )

    with st.sidebar:
        st.header("Quick Fill")
        if st.button("Load ancestor sample"):
            st.session_state["facts_input"] = DEFAULT_FACTS
            st.session_state["rules_input"] = DEFAULT_RULES
            st.session_state["query_input"] = DEFAULT_QUERY
        st.write("Facts syntax: parent(alice,bob) one per line.")
        st.write(
            "Rules syntax: \\forall x,y: parent(x,y) -> ancestor(x,y); use & for "
            "conjunction."
        )
        st.write(
            "Use ?var or bare variable names in rules; they will be converted to "
            "Stage 4 format."
        )

    facts_default = st.session_state.get("facts_input", DEFAULT_FACTS)
    rules_default = st.session_state.get("rules_input", DEFAULT_RULES)
    query_default = st.session_state.get("query_input", DEFAULT_QUERY)

    with st.form("kb_form"):
        facts_text = st.text_area(
            "Facts",
            value=facts_default,
            height=160,
            key="facts_input",
        )
        rules_text = st.text_area(
            "Rules",
            value=rules_default,
            height=160,
            key="rules_input",
        )
        query_text = st.text_input(
            "Query pattern",
            value=query_default,
            key="query_input",
        )
        submitted = st.form_submit_button("Run reasoning")

    if submitted:
        try:
            facts = parse_facts_block(facts_text)
            rules = parse_rules_block(rules_text)
            query = parse_query(query_text)
        except ParseError as err:
            st.error(str(err))
            st.stop()

        kb = KB(facts=facts, rules=rules)
        kb.forward_chain()
        st.success(f"Reasoner finished with {len(kb.facts)} total facts.")

        st.subheader("Facts")
        st.write(
            "Initial facts are shown first; new derivations are highlighted."
        )
        input_fact_set = set(facts)
        derived_rows = []
        for fact in sorted(kb.facts):
            derived_rows.append(
                {
                    "predicate": fact[0],
                    "arguments": fact[1:],
                    "source": "derived" if fact not in input_fact_set else "given",
                }
            )
        st.dataframe(derived_rows, use_container_width=True)

        st.subheader("Query Results")
        answers = kb.query(query)
        if answers:
            display = [
                {var: val for var, val in sorted(ans.items())}
                for ans in answers
            ]
            st.table(display)
        else:
            st.info("No matches for the query pattern.")


if __name__ == "__main__":
    main()