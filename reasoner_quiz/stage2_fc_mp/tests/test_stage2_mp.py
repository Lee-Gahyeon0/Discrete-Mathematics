from reasoner import KB


def test_mp_chain():
    kb = KB(facts={"P"}, rules=[("IMPLIES", "P", "Q"), ("IMPLIES", "Q", "R")])
    kb.forward_chain()
    assert "Q" in kb.facts and "R" in kb.facts

