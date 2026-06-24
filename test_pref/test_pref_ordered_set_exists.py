from pref import __author__, PrefOrderedSet

from test_pref import __application_name__


def test_exists_distinguishes_unset_from_empty():
    with PrefOrderedSet(__application_name__, __author__, "selection") as s:
        # never written
        assert s.exists() is False
        assert s.get(default=None) is None
        assert s.get(default=["fallback"]) == ["fallback"]
        assert s.get() == []  # no-arg back-compat: empty list, not the default

        # explicitly set to empty
        s.set([])
        assert s.exists() is True
        assert s.get() == []
        assert s.get(default=["fallback"]) == []  # exists() True -> ignore default
