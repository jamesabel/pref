from attr import attrib, attrs
from pref import __author__, Pref

from test_pref import __application_name__


@attrs
class PrefTst(Pref):
    my_variable = attrib(default=None)


def test_preferences():
    file_name = "user_provided_file_name.db"

    preferences = PrefTst(__application_name__, __author__, file_name=file_name)
    assert preferences.get_sqlite_path().exists()
    my_value = "me"
    preferences.my_variable = my_value

    preferences = PrefTst(__application_name__, __author__, file_name=file_name)
    assert preferences.my_variable == my_value
