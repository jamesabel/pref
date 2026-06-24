from attr import attrib, attrs

from pref import __author__, Pref, PrefOrderedSet

from test_pref import __application_name__


@attrs
class PrefTst(Pref):
    my_variable = attrib(default=None)


def test_ordered_set_context_manager_persists_and_closes():
    with PrefOrderedSet(__application_name__, __author__, "selection") as s:
        s.set(["a", "b"])
    # handle closed; reopening reads the persisted data
    with PrefOrderedSet(__application_name__, __author__, "selection") as readback:
        assert readback.get() == ["a", "b"]


def test_ordered_set_explicit_close():
    s = PrefOrderedSet(__application_name__, __author__, "selection")
    s.add("x")
    s.close()  # explicit close should not raise


def test_pref_context_manager():
    with PrefTst(__application_name__, __author__) as p:  # close() is a no-op for Pref
        p.my_variable = "ctx"
    assert PrefTst(__application_name__, __author__).my_variable == "ctx"
