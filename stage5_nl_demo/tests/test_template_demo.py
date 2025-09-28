from template_demo import TemplateEngine, run_demo


def test_templates_render_expected_logic():
    engine = TemplateEngine()
    fact = engine.render("parent_fact", parent="Alice", child="Bob")
    rule = engine.render("parent_rule")
    trans = engine.render("ancestor_transitivity")

    assert fact == ("parent", "alice", "bob")
    assert rule[0] == "FORALL"
    assert trans[0] == "FORALL"


def test_demo_produces_inferred_ancestor():
    results, kb = run_demo()
    assert any(
        result.valid for result in results if "ancestor of Carol" in result.text
    )
    assert ("ancestor", "alice", "carol") in kb.facts


def test_query_template_lists_targets():
    engine = TemplateEngine()
    pattern = engine.render("ancestor_query", target="Carol")
    assert pattern == ("ancestor", "?who", "carol")