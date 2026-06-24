from pref import __author__, PrefOrderedSet

from test_pref import __application_name__


def test_add_discard_and_membership():
    with PrefOrderedSet(__application_name__, __author__, "selection") as s:
        s.add("a")
        s.add("b")
        s.add("a")  # dedup, no reorder
        assert s.get() == ["a", "b"]
        assert "a" in s
        assert "z" not in s
        assert len(s) == 2
        assert list(s) == ["a", "b"]

        s.discard("a")
        assert "a" not in s
        assert s.get() == ["b"]
        s.discard("not-there")  # no-op
        assert s.get() == ["b"]


def test_add_marks_set_as_configured():
    with PrefOrderedSet(__application_name__, __author__, "selection") as s:
        assert s.exists() is False
        s.add("x")
        assert s.exists() is True
