import pytest
import shutil

from pref import __author__, Pref

from test_pref import __application_name__


@pytest.fixture(autouse=True)
def remove_db():
    pref = Pref(__application_name__, __author__)
    sqlite_path = pref.get_sqlite_path()
    shutil.rmtree(sqlite_path.parent)
