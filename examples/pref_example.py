from attr import attrib, attrs
from ismain import is_main

from pref import PrefDict, PrefOrderedSet

application_name = "myapp"
author = "me"

@attrs
class MyPref(PrefDict):
    name = attrib(default=None)


if is_main():

    # set a variable
    preferences = MyPref(application_name, author)
    preferences.name = "me"

    # read it back
    preferences = MyPref(application_name, author)
    print(preferences.name)  # me

    # set an ordered set (list-like, but no duplicates)
    my_list = PrefOrderedSet(application_name, author, "mylist")
    my_list.set(["a", "b", "c"])

    # read the ordered set back in
    my_list = PrefOrderedSet(application_name, author, "mylist")
    print(my_list.get())  # ['a', 'b', 'c']
