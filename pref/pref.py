from pathlib import Path
from typing import List
import warnings

import appdirs
from sqlitedict import SqliteDict
from attr import attrib, attrs


def get_sqlite_path(name: str, author: str) -> Path:
    sqlite_path = Path(appdirs.user_config_dir(name, author), f"{name}.db")
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite_path


class _PreferenceConstant(str):
    """
    Values of type PreferenceConstant don't get written to the DB
    """


def _to_preferences_constant(s):
    return _PreferenceConstant(s)


@attrs
class Pref:
    """
    store/retrieve preferences as a set of attrs attributes to/from a sqlite database
    """

    application_name = attrib(type=_PreferenceConstant, converter=_to_preferences_constant)
    application_author = attrib(type=_PreferenceConstant, converter=_to_preferences_constant)
    table = attrib(default="preferences", type=_PreferenceConstant, converter=_to_preferences_constant)
    __pref__init__done__ = False  # fairly unique, reserved key

    def __attrs_post_init__(self):
        # initialize values from the DB for the derived class's attributes
        sqlite_dict = self.get_sqlite_dict()
        for key in self.__dict__:
            value = sqlite_dict.get(key)
            if value is not None and not isinstance(value, _PreferenceConstant):
                super().__setattr__(key, value)  # only call super since we don't have to worry about updating the DB here
        self.__pref__init__done__ = True  # gets written to the database

    def __setattr__(self, key, value):
        # update the DB for a (potentially) new value of a derived class's attribute
        super().__setattr__(key, value)
        if self.__pref__init__done__ and not isinstance(value, _PreferenceConstant) and value is not None:
            # only write to the DB if data has changed
            sql_lite_dict = self.get_sqlite_dict()
            existing_value = sql_lite_dict.get(key)
            if existing_value != value:
                sql_lite_dict[key] = value  # does the DB write

    def get_sqlite_dict(self) -> SqliteDict:
        return SqliteDict(get_sqlite_path(self.application_name, self.application_author), self.table, autocommit=True, encode=lambda x: x, decode=lambda x: x)


# legacy
class PrefDict(Pref):
    def __attrs_post_init__(self):
        warnings.warn("use Pref class instead of PrefDict", DeprecationWarning)
        super().__attrs_post_init__()


class PrefOrderedSet:
    """
    store/retrieve an ordered set of strings (like a list, but no duplicates) to/from a sqlite database
    """

    def __init__(self, name: str, author: str, table: str):
        # DB stores values directly (not encoded as a pickle)
        self.sqlite_dict = SqliteDict(get_sqlite_path(name, author), table, encode=lambda x: x, decode=lambda x: x)

    def set(self, strings: list):
        """
        set the list of strings
        :param strings: list of strings
        """
        self.sqlite_dict.clear()  # delete entire table
        # ordering is done by making the value in the key/value pair the index and our desired list "value" is the key
        for index, string in enumerate(strings):
            self.sqlite_dict[string] = index
        self.sqlite_dict.commit()  # not using autocommit since we're updating (setting) multiple values in the above for loop

    def get(self) -> List[str]:
        """
        returns the list of strings
        :return: list of strings
        """
        return list(sorted(self.sqlite_dict, key=self.sqlite_dict.get))
