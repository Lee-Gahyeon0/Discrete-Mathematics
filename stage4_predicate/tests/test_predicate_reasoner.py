from reasoner import KB, unify


def test_transitive_ancestor():
    kb = KB(
        facts=[
            ("parent", "alice", "bob"),
            ("parent", "bob", "carol"),
        ],
        rules=[
            (
                "FORALL",
                ["?x", "?y"],
                (
                    "IMPLIES",
                    [("parent", "?x", "?y")],
                    ("ancestor", "?x", "?y"),
                ),
            ),
            (
                "FORALL",
                ["?x", "?y", "?z"],
                (
                    "IMPLIES",
                    [("parent", "?x", "?y"), ("ancestor", "?y", "?z")],
                    ("ancestor", "?x", "?z"),
                ),
            ),
        ],
    )
    kb.forward_chain()
    assert ("ancestor", "alice", "bob") in kb.facts
    assert ("ancestor", "alice", "carol") in kb.facts


def test_existential_conclusions_create_skolem_constants():
    kb = KB(
        facts=[("parent", "mia")],
        rules=[
            (
                "FORALL",
                ["?x"],
                (
                    "IMPLIES",
                    [("parent", "?x")],
                    ("EXISTS", ["?y"], ("loves", "?x", "?y")),
                ),
            )
        ],
    )
    kb.forward_chain()
    matches = [fact for fact in kb.facts if fact and fact[0] == "loves"]
    assert len(matches) == 1
    lover, beloved = matches[0][1], matches[0][2]
    assert lover == "mia"
    assert not beloved.startswith("?")
    assert beloved.startswith("_sk")


def test_query_returns_substitutions():
    kb = KB(
        facts=[
            ("ancestor", "alice", "carol"),
            ("ancestor", "mia", "larry"),
        ]
    )
    answers = kb.query(("ancestor", "?who", "carol"))
    assert any(ans.get("?who") == "alice" for ans in answers)
    assert all("?who" in ans for ans in answers)


def test_unify_handles_nested_structures():
    left = ("likes", "?x", ("pair", "?x", "?y"))
    right = ("likes", "mia", ("pair", "mia", "cello"))
    result = unify(left, right, {})
    assert result == {"?x": "mia", "?y": "cello"}