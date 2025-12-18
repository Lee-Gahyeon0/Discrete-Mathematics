import pytest

from app import (
    DEFAULT_FACTS,
    DEFAULT_QUERY,
    parse_fact,
    parse_facts_block,
    parse_query,
    parse_rule,
    parse_rules_block,
)


def test_parse_fact_round_trips_defaults():
    facts = parse_facts_block(DEFAULT_FACTS)
    assert ("parent", "alice", "bob") in facts


def test_parse_rule_handles_conjunction():
    rule = parse_rule(
        "forall x,y,z: parent(x,y) & ancestor(y,z) -> ancestor(x,z)"
    )
    assert rule[0] == "FORALL"
    assert len(rule[2][0]) == 2


def test_parse_query_accepts_variables():
    pattern = parse_query(DEFAULT_QUERY)
    assert pattern == ("ancestor", "?who", "dana")


def test_parse_invalid_fact_raises():
    with pytest.raises(Exception):
        parse_fact("invalid fact")


def test_rules_block_ignores_blank_lines():
    rules = parse_rules_block("""forall x: parent(x) -> ancestor(x)\n\n""")
    assert len(rules) == 1
