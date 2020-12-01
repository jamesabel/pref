from copy import deepcopy

from attr import attrib, attrs
from pref import __author__, PrefDict, PrefList

from test_pref import __application_name__


@attrs
class PrefTst(PrefDict):
    my_variable = attrib(default=None)


def test_preferences():
    preferences = PrefTst(__application_name__, __author__)
    my_value = "me"
    preferences.my_variable = my_value

    preferences = PrefTst(__application_name__, __author__)
    assert preferences.my_variable == my_value

    exclusions = PrefList(__application_name__, __author__, "exclusions")
    test_list = ["a", "b", "a", "", "qwertyuiop", "c", 1]  # two "a"s, and an int 1
    expected_results = deepcopy(test_list)
    expected_results.pop(0)  # remove 1st "a"
    expected_results[-1] = str(expected_results[-1])  # the input value can be non-string, but it'll be returned as a string
    exclusions.set(test_list)
    assert exclusions.get() == expected_results
