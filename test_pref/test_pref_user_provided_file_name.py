from attr import attrib, attrs
from pref import __author__, Pref, get_sqlite_path

from test_pref import __application_name__


@attrs
class PrefTst(Pref):
    my_variable = attrib(default=None)


def test_preferences():
    file_name = "user_provided_file_name.db"
    sql_lite_path = get_sqlite_path(__application_name__, __author__, file_name)
    print(f"{sql_lite_path=}")
    assert not sql_lite_path.exists()  # pytest fixture deletes the sqlite file

    preferences = PrefTst(__application_name__, __author__, file_name=file_name)
    assert get_sqlite_path(__application_name__, __author__, file_name).exists()
    my_value = "me"
    preferences.my_variable = my_value

    preferences = PrefTst(__application_name__, __author__, file_name=file_name)
    assert preferences.my_variable == my_value
