from attr import attrib, attrs

from pref import __author__, Pref, get_sqlite_path

from test_pref import __application_name__

my_default_string = "my default string"
my_new_string = "I am new"


@attrs
class PrefTst(Pref):
    my_bool: bool = attrib(default=True)
    my_other_bool: bool = attrib(default=False)
    my_str: bool = attrib(default=my_default_string)


def test_preferences():
    assert not get_sqlite_path(__application_name__, __author__).exists()  # check that the testing framework starts without at DB file
    preferences = PrefTst(__application_name__, __author__)

    assert preferences.my_bool
    assert not preferences.my_other_bool
    assert preferences.my_str == my_default_string

    preferences.my_bool = False
    preferences.my_str = my_new_string
    assert not preferences.my_bool
    assert not preferences.my_other_bool
    assert preferences.my_str == my_new_string

    preferences.my_other_bool = False
    assert not preferences.my_other_bool
