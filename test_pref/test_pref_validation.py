import logging
from pathlib import Path

import attr
import pytest
from attr import attrib, attrs
from sqlitedict import SqliteDict

from pref import __author__, Pref

from test_pref import __application_name__


@attrs
class Bounded(Pref):
    poll_seconds: float = attrib(default=2.0, converter=float, validator=attr.validators.ge(0.5))
    name: str = attrib(default="", converter=str)


def test_converter_and_validator_run_on_set(tmp_path: Path):
    preferences = Bounded(__application_name__, __author__, config_dir=tmp_path)
    preferences.poll_seconds = "3"  # converted before validation and storage
    assert preferences.poll_seconds == 3.0 and isinstance(preferences.poll_seconds, float)
    with pytest.raises(ValueError):
        preferences.poll_seconds = 0.1  # below the validator's bound
    assert preferences.poll_seconds == 3.0  # neither set nor stored
    assert Bounded(__application_name__, __author__, config_dir=tmp_path).poll_seconds == 3.0
    preferences.name = 42
    assert Bounded(__application_name__, __author__, config_dir=tmp_path).name == "42"


def test_stored_value_that_no_longer_validates_falls_back_to_the_default(tmp_path: Path, caplog):
    preferences = Bounded(__application_name__, __author__, config_dir=tmp_path)
    preferences.poll_seconds = 4.0
    path = preferences.get_sqlite_path()
    with SqliteDict(path, "preferences", autocommit=True, encode=lambda x: x, decode=lambda x: x) as raw:
        raw["poll_seconds"] = 0.01  # a hand-edited file, or an older version's range
    with caplog.at_level(logging.WARNING, logger="pref.pref"):
        loaded = Bounded(__application_name__, __author__, config_dir=tmp_path)
    assert loaded.poll_seconds == 2.0  # the default, not the stored value
    assert "rejected" in caplog.text
