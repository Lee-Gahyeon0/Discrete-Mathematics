import pytest

from kb import KB, is_atom, is_not, negate


def test_add_and_conflict():
    kb = KB()
    assert kb.add_fact("P")
    assert not kb.add_fact("P")
    with pytest.raises(ValueError):
        kb.add_fact(("NOT", "P"))


def test_negate():
    assert negate("Q") == ("NOT", "Q")
    assert negate(("NOT", "Q")) == "Q"

