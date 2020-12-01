from attr import attrib, attrs
from pref import PrefDict, PrefOrderedSet
from ismain import is_main

application_name = "myapp"
author = "me"

@attrs
class MyPref(PrefDict):
    name = attrib(default=None)


if is_main():
    preferences = MyPref(application_name, author)
    preferences.name = "me"

    preferences = MyPref(application_name, author)
    print(preferences.name)  # me

    my_list = PrefOrderedSet(application_name, author, "mylist")
    my_list.set(["a", "b", "c"])

    my_list = PrefOrderedSet(application_name, author, "mylist")
    print(my_list.get())  # ['a', 'b', 'c']
