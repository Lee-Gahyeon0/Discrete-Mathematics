from reasoner import KB


def test_all():
    kb = KB(
        facts={"P", ("OR", "P", "Q"), ("AND", "P", ("NOT", "R"))},
        rules=[
            ("IMPLIES", "P", "R"),
            ("IMPLIES", "Q", "T"),
            ("IMPLIES", "R", "U"),
            ("IMPLIES", "T", "V"),
        ],
    )
    kb.forward_chain()
    assert ("IMPLIES", "P", "U") in kb.rules and ("IMPLIES", "Q", "V") in kb.rules
    assert "R" in kb.facts and "U" in kb.facts
