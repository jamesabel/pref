from attr import attrib, attrs

from pref import __author__, Pref, PrefOrderedSet

from test_pref import __application_name__


@attrs
class PrefTst(Pref):
    my_variable = attrib(default=None)


def test_tables_lists_the_data_table():
    with PrefOrderedSet(__application_name__, __author__, "houses") as s:
        s.set(["a", "b"])
        assert "houses" in s.tables()


def test_clear_resets_to_unset():
    with PrefOrderedSet(__application_name__, __author__, "houses") as s:
        s.set(["a", "b"])
        s.clear()
        assert s.get() == []
        assert s.exists() is False  # clear() resets to "never written"


def test_reset_restores_defaults():
    pref = PrefTst(__application_name__, __author__)
    pref.my_variable = "to-be-reset"
    pref.reset()
    # a freshly constructed instance falls back to the default
    assert PrefTst(__application_name__, __author__).my_variable is None
