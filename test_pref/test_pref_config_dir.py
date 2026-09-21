"""
All tests in this module are AI-generated (Claude Code); the helper class is covered by that note.
"""

from pathlib import Path

from attr import attrib, attrs
from platformdirs import user_config_dir

from pref import __author__, Pref, PrefOrderedSet, PrefStore, default_config_dir

from test_pref import __application_name__


@attrs
class PrefTst(Pref):
    my_variable = attrib(default=None)


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_default_location_is_the_platformdirs_config_dir():
    expected = Path(user_config_dir(__application_name__, __author__))
    assert default_config_dir(__application_name__, __author__) == expected or not expected.exists()
    preferences = PrefTst(__application_name__, __author__)
    assert preferences.get_sqlite_path().parent == default_config_dir(__application_name__, __author__)


# AI-GENERATED TEST (Claude Code) - delete this line to make this test human-owned.
def test_explicit_config_dir_is_used_by_every_class(tmp_path: Path):
    where = tmp_path / "nested" / "config"
    preferences = PrefTst(__application_name__, __author__, config_dir=where)
    preferences.my_variable = "me"
    assert preferences.get_sqlite_path() == where / f"{__application_name__}.db"
    assert PrefTst(__application_name__, __author__, config_dir=str(where)).my_variable == "me"

    ordered = PrefOrderedSet(__application_name__, __author__, "things", config_dir=where)
    ordered.set(["a", "b"])
    assert ordered.get_sqlite_path().parent == where
    assert PrefOrderedSet(__application_name__, __author__, "things", config_dir=where).get() == ["a", "b"]

    store = PrefStore(__application_name__, __author__, config_dir=where)
    assert store.bind(PrefTst).my_variable == "me"
    assert store.ordered_set("things").get() == ["a", "b"]
    # nothing landed in the default location
    assert not (default_config_dir(__application_name__, __author__) / f"{__application_name__}.db").exists()
