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


class _PreferenceMeta:
    """
    Values of type _PreferenceMeta (or derived classes) don't get written to the DB
    """


class _PreferenceMetaStr(_PreferenceMeta, str):
    ...


class _PreferenceMetaBool(_PreferenceMeta, int):
    ...


def _to_preferences_meta_str(s):
    return _PreferenceMetaStr(s)


@attrs
class Pref:
    """
    store/retrieve preferences as a set of attrs attributes to/from a sqlite database
    """

    application_name = attrib(type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    application_author = attrib(type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    table = attrib(default="preferences", type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    pref_init = _PreferenceMetaBool(False)  # starts as a class variable, then set to True as a class instance variable once all initialization is complete

    def __attrs_post_init__(self):
        # initialize values from the DB for the derived class's attributes
        sqlite_dict = self.get_sqlite_dict()
        for key in self.__dict__:
            value = sqlite_dict.get(key)
            if value is not None and not isinstance(value, _PreferenceMeta):
                super().__setattr__(key, value)  # only call super since we don't have to worry about updating the DB here
        self.pref_init = _PreferenceMetaBool(True)  # now a class instance variable (no longer a class variable)

    def __setattr__(self, key, value):
        # update the DB for a (potentially) new value of a derived class's attribute
        super().__setattr__(key, value)
        if self.pref_init and not isinstance(value, _PreferenceMeta):
            # only write to the DB if data has changed
            sql_lite_dict = self.get_sqlite_dict()
            existing_value = sql_lite_dict.get(key)
            if existing_value != value:
                sql_lite_dict[key] = value  # does the DB write

    def get_sqlite_dict(self) -> SqliteDict:
        # override this method if you don't like this "pass through" encoding, or want a different sqlite file path, etc.
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
