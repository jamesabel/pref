from pathlib import Path
from typing import List

import appdirs
from sqlitedict import SqliteDict
from attr import attrib, attrs


class _PreferenceMeta:
    """
    Values of type _PreferenceMeta (or derived classes) don't get written to the DB
    """


class _PreferenceMetaStr(_PreferenceMeta, str):
    pass


class _PreferenceMetaBool(_PreferenceMeta, int):
    pass


def _to_preferences_meta_str(s: str):
    return _PreferenceMetaStr(s)


class SQLitePath:

    def __init__(self, application_name: str, application_author: str, file_name: str | None):
        self.application_name = application_name
        self.application_author = application_author
        self.file_name = file_name

    def get_sqlite_path(self) -> Path:
        if self.file_name is None or len(self.file_name) < 1:
            self.file_name = f"{self.application_name}.db"
        assert "." in self.file_name, f'file_name must have a file extension (e.g., ".db"): "{self.file_name=}"'
        sqlite_path = Path(appdirs.user_config_dir(self.application_name, self.application_author), self.file_name)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite_path


@attrs
class Pref(SQLitePath):
    """
    store/retrieve preferences as a set of attrs attributes to/from a sqlite database
    """

    application_name = attrib(type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    application_author = attrib(type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    table = attrib(default=_PreferenceMetaStr("preferences"), type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    file_name = attrib(default=_PreferenceMetaStr(""), type=_PreferenceMetaStr, converter=_to_preferences_meta_str)  # default of "" means use f"{application_name}.db"
    _pref_init = _PreferenceMetaBool(False)  # starts as a class variable, then set to True as a class instance variable once all initialization is complete

    def __attrs_post_init__(self):
        # initialize values from the DB for the derived class's attributes
        sqlite_dict = self.get_sqlite_dict()
        for key in self.__dict__:
            value = sqlite_dict.get(key)
            if value is not None and not isinstance(value, _PreferenceMeta):
                super().__setattr__(key, value)  # only call super since we don't have to worry about updating the DB here
        self._pref_init = _PreferenceMetaBool(True)  # now a class instance variable (no longer a class variable)

    def __setattr__(self, key, value):
        # update the DB for a (potentially) new value of a derived class's attribute
        super().__setattr__(key, value)
        if self._pref_init and not isinstance(value, _PreferenceMeta):
            sql_lite_dict = self.get_sqlite_dict()
            existing_value = sql_lite_dict.get(key)
            # only write to the DB if data has changed
            if existing_value != value:
                sql_lite_dict[key] = value  # does the DB write

    def get_sqlite_dict(self) -> SqliteDict:
        # override this method if you don't like this "pass through" encoding, or want a different sqlite file path, etc.
        sqlite_path = self.get_sqlite_path()
        return SqliteDict(sqlite_path, self.table, autocommit=True, encode=lambda x: x, decode=lambda x: x)


class PrefOrderedSet(SQLitePath):
    """
    store/retrieve an ordered set of strings (like a list, but no duplicates) to/from a sqlite database
    """

    def __init__(self, application_name: str, application_author: str, table: str, file_name: str | None = None):
        """
        :param application_name: name of the application
        :param application_author: name of the application author
        :param table: name of the data group (used as the sqlite table)
        :param file_name: optional name of the sqlite file
        """
        super().__init__(application_name, application_author, file_name)
        # DB stores values directly (not encoded as a pickle)
        self.application_name = application_name
        self.application_author = application_author
        self.file_name = file_name
        sqlite_path = self.get_sqlite_path()
        self.sqlite_dict = SqliteDict(sqlite_path, table, encode=lambda x: x, decode=lambda x: x)

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
