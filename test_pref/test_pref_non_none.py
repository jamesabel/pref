from attr import attrib, attrs

from pref import __author__, Pref

from test_pref import __application_name__

my_default_string = "my default string"
my_new_string = "I am new"


@attrs
class PrefTst(Pref):
    my_bool: bool = attrib(default=True)
    my_other_bool: bool = attrib(default=False)
    my_str: str = attrib(default=my_default_string)


def test_preferences():

    preferences = PrefTst(__application_name__, __author__)

    assert preferences.my_bool
    assert not preferences.my_other_bool
    assert preferences.my_str == my_default_string

    preferences.my_bool = False  # was True, now set to False
    preferences.my_str = my_new_string
    assert not preferences.my_bool
    assert not preferences.my_other_bool
    assert preferences.my_str == my_new_string

    preferences.my_other_bool = False  # same value as default - should not even write to DB
    assert not preferences.my_other_bool

    # now make sure what we wrote is still in the DB
    preferences = PrefTst(__application_name__, __author__)
    assert not preferences.my_bool
    assert not preferences.my_other_bool
    assert preferences.my_str == my_new_string
