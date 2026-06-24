import sqlite3
from pathlib import Path
from typing import List, Optional

import appdirs
from sqlitedict import SqliteDict
from attr import attrib, attrs

# sentinel used to distinguish "caller passed no default" from "caller passed default=None"
_UNSET = object()


class _PreferenceMeta:
    """
    Values of type _PreferenceMeta (or derived classes) don't get written to the DB
    """


class _PreferenceMetaStr(_PreferenceMeta, str):
    pass


class _PreferenceMetaBool(_PreferenceMeta, int):
    pass


def _to_preferences_meta_str(s):
    # None/falsy maps to "" so that the get_sqlite_path() default-file-name logic kicks in
    # (without this, a None file_name would be converted to the literal string "None")
    if s is None:
        s = ""
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

    def tables(self) -> List[str]:
        """
        :return: the list of table names present in this store's sqlite file
        """
        # Note: we deliberately do NOT use SqliteDict.get_tablenames() here. That helper opens a
        # `with sqlite3.connect(...)` which commits but never closes the connection, leaking a file
        # handle that blocks deleting the DB on Windows. We open and close the connection ourselves.
        sqlite_path = self.get_sqlite_path()
        conn = sqlite3.connect(sqlite_path)
        try:
            rows = conn.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
        finally:
            conn.close()
        return [row[0] for row in rows]


@attrs
class Pref(SQLitePath):
    """
    store/retrieve preferences as a set of attrs attributes to/from a sqlite database
    """

    application_name = attrib(type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    application_author = attrib(type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    table = attrib(default=_PreferenceMetaStr("preferences"), type=_PreferenceMetaStr, converter=_to_preferences_meta_str)
    file_name = attrib(default=None, type=_PreferenceMetaStr, converter=_to_preferences_meta_str)  # default of None/"" means use f"{application_name}.db"
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

    def reset(self) -> None:
        """
        Delete this preference group's table so attributes fall back to their defaults.
        """
        sqlite_dict = self.get_sqlite_dict()
        sqlite_dict.clear()
        sqlite_dict.commit()

    def close(self) -> None:
        # Pref opens a fresh autocommit handle per access (see get_sqlite_dict), so there is no
        # long-lived handle to close. Provided for symmetry with PrefOrderedSet / context-manager use.
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


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
        self.table = table
        self.file_name = file_name
        sqlite_path = self.get_sqlite_path()
        self.sqlite_dict = SqliteDict(sqlite_path, table, encode=lambda x: x, decode=lambda x: x)
        # companion meta table records whether this set has ever been written, so callers can
        # tell "never set" apart from "set to empty" (the value table is empty in both cases)
        self._meta = SqliteDict(sqlite_path, f"{table}__meta", encode=lambda x: x, decode=lambda x: x)

    def _mark_configured(self):
        self._meta["configured"] = 1
        self._meta.commit()

    def exists(self) -> bool:
        """
        :return: True if this set was ever written (via set()/add()), even if it was set to empty
        """
        return self._meta.get("configured") is not None

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
        self._mark_configured()

    def get(self, default=_UNSET) -> List[str]:
        """
        returns the list of strings
        :param default: value to return if this set was never written (only used when explicitly passed)
        :return: list of strings, or `default` if never written and `default` was provided
        """
        if not self.exists() and default is not _UNSET:
            return default
        return list(sorted(self.sqlite_dict, key=self.sqlite_dict.get))

    def add(self, s: str) -> None:
        """
        add a single string to the set (no-op if already present); preserves insertion order
        """
        if s not in self.sqlite_dict:
            self.sqlite_dict[s] = len(self.sqlite_dict)  # append at end
            self.sqlite_dict.commit()
        self._mark_configured()

    def discard(self, s: str) -> None:
        """
        remove a single string from the set (no-op if not present)
        """
        if s in self.sqlite_dict:
            del self.sqlite_dict[s]  # index gaps are fine; get() sorts by the stored index
            self.sqlite_dict.commit()

    def clear(self) -> None:
        """
        remove all strings and reset this set to the "never written" state (exists() becomes False)
        """
        self.sqlite_dict.clear()
        self.sqlite_dict.commit()
        self._meta.clear()
        self._meta.commit()

    def close(self) -> None:
        self.sqlite_dict.close()
        self._meta.close()

    def __contains__(self, s: str) -> bool:
        return s in self.sqlite_dict

    def __len__(self) -> int:
        return len(self.sqlite_dict)

    def __iter__(self):
        return iter(self.get())

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class PrefStore:
    """
    factory that holds the application identity once so PrefOrderedSet / Pref instances
    can be created without repeating (application_name, application_author, file_name)
    """

    def __init__(self, application_name: str, application_author: str, file_name: Optional[str] = None):
        self.application_name = application_name
        self.application_author = application_author
        self.file_name = file_name

    def ordered_set(self, table: str) -> PrefOrderedSet:
        return PrefOrderedSet(self.application_name, self.application_author, table, self.file_name)

    def bind(self, pref_cls):
        """
        construct a Pref subclass bound to this store's identity
        :param pref_cls: a Pref subclass
        """
        return pref_cls(self.application_name, self.application_author, file_name=self.file_name or "")
