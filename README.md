# pref - a simple local preferences store

Since 0.5:

- **Where the file lives.** By default the per-user config directory from `platformdirs`
  (e.g. `%LOCALAPPDATA%\\author\\myapp` on Windows, `~/.config/myapp` on Linux). Pass
  `config_dir=` to `Pref`, `PrefOrderedSet` or `PrefStore` to put it anywhere else, such as
  beside an application's own data files. On macOS a directory left by pref 0.4 under
  `~/Library/Preferences` keeps being used.
- **Validation and conversion.** An attribute's `attrs` `converter` and `validator` run on every
  set and on every load, not only at construction: a rejected value raises on set and is
  neither stored nor kept, and a stored value that no longer validates (a hand-edited file,
  an older version's range) falls back to the default with a warning.

```
@attrs
class MyPref(Pref):
    poll_seconds: float = attrib(default=2.0, converter=float, validator=attr.validators.ge(0.5))
```


Persistent storage of `attrs` attributes or an ordered set (like a list, but no duplicates) to 
a local SQLite database file. 

# Example

```
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
```
