from .__version__ import __application_name__, __author__, __version__, __url__, __title__, __description__, __download_url__, __author_email__
from .pref import Pref, PrefOrderedSet, PrefStore, SQLitePath, default_config_dir

__all__ = [
    "Pref",
    "PrefOrderedSet",
    "PrefStore",
    "SQLitePath",
    "default_config_dir",
    "__application_name__",
    "__author__",
    "__author_email__",
    "__description__",
    "__download_url__",
    "__title__",
    "__url__",
    "__version__",
]
