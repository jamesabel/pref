from attr import attrib, attrs

from pref import __author__, Pref, PrefOrderedSet, PrefStore

from test_pref import __application_name__


@attrs
class PrefTst(Pref):
    my_variable = attrib(default=None)


def test_pref_store_factory():
    store = PrefStore(__application_name__, __author__)

    with store.ordered_set("group_a") as os_a:
        os_a.set(["one", "two"])
    with PrefOrderedSet(__application_name__, __author__, "group_a") as readback:
        assert readback.get() == ["one", "two"]

    pref = store.bind(PrefTst)
    pref.my_variable = "bound"
    assert PrefTst(__application_name__, __author__).my_variable == "bound"
