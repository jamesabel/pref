from attr import attrib, attrs
from ismain import is_main

from pref import Pref, PrefOrderedSet

application_name = "myapp"
author = "me"


@attrs
class MyPref(Pref):
    first_name: str = attrib(default=None)
    last_name: str = attrib(default=None)
    has_subscription: bool = attrib(default=False)  # start off with no subscription


def get_pref() -> MyPref:
    return MyPref(application_name, author)


def get_ordered_set() -> PrefOrderedSet:
    return PrefOrderedSet(application_name, author, "mylist")


if is_main():

    # set a variable
    preferences = get_pref()
    preferences.first_name = "James"
    preferences.last_name = "Abel"

    # read it back
    preferences = get_pref()
    print(preferences.first_name)  # James
    print(preferences.last_name)  # Abel
    print(preferences.has_subscription)  # evaluates as False (is actually int of 0)

    # set an ordered set (list-like, but no duplicates)
    my_list = get_ordered_set()
    my_list.set(["a", "b", "c"])

    # read the ordered set back in
    my_list = get_ordered_set()
    print(my_list.get())  # ['a', 'b', 'c']
