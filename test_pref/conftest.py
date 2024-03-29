import pytest
import shutil

from pref import __author__, get_sqlite_path

from test_pref import __application_name__


@pytest.fixture(autouse=True)
def remove_db():
    sqlite_path = get_sqlite_path(__application_name__, __author__)
    shutil.rmtree(sqlite_path.parent)
