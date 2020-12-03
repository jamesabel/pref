# pref - a simple local preferences store

Persistent storage of `attrs` attributes or an ordered set (like a list, but no duplicates) to 
a local SQLite database file. 

# Example

```
from attr import attrib, attrs
from ismain import is_main

from pref import PrefDict, PrefOrderedSet

application_name = "myapp"
author = "me"


@attrs
class MyPref(PrefDict):
    name = attrib(default=None)


def get_pref() -> MyPref:
    return MyPref(application_name, author)


def get_ordered_set() -> PrefOrderedSet:
    return PrefOrderedSet(application_name, author, "mylist")


if is_main():

    # set a variable
    preferences = get_pref()
    preferences.name = "me"

    # read it back
    preferences = get_pref()
    print(preferences.name)  # me

    # set an ordered set (list-like, but no duplicates)
    my_list = get_ordered_set()
    my_list.set(["a", "b", "c"])

    # read the ordered set back in
    my_list = get_ordered_set()
    print(my_list.get())  # ['a', 'b', 'c']
```
