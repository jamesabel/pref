from attr import attrib, attrs

from pref import __author__, Pref

from test_pref import __application_name__


@attrs
class PrefTst(Pref):
    my_variable = attrib(default=None)


def test_pref_file_name_defaults_to_app_db():
    # Pref.file_name defaults to None (converted to ""), matching PrefOrderedSet's default,
    # so the sqlite file name falls back to f"{application_name}.db".
    p = PrefTst(__application_name__, __author__)
    assert p.get_sqlite_path().name == f"{__application_name__}.db"
