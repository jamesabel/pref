# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`pref` is a small Python library that persists application preferences to a local
SQLite database. It exposes two classes (see `pref/pref.py`):

- `Pref` — an `attrs`-based class users subclass to declare typed preference attributes;
  reads/writes are transparently synced to SQLite on attribute access.
- `PrefOrderedSet` — stores an ordered set of strings (list semantics, no duplicates).

Both back onto SQLite via `sqlitedict`, and locate their DB file under the OS's
per-user config dir via `appdirs` (`SQLitePath.get_sqlite_path()`).

## Common commands

The dev workflow assumes a `venv/` created by the scripts below (the `.bat` files
hardcode `venv\Scripts\...` and activate it). On non-Windows shells, replicate the
single relevant command rather than running the batch file.

- Create the dev venv: `scripts\make_venv_dev.bat` (uses Python 3.14, installs `requirements-dev.txt`)
- Run tests: `venv\Scripts\pytest.exe` (set `PYTHONPATH=%CD%` first, as `scripts\coverage.bat` does)
- Run a single test: `venv\Scripts\pytest.exe test_pref/test_pref_simple.py::test_preferences`
- Coverage (HTML + XML): `scripts\coverage.bat`
- Format: `scripts\blackify.bat` — **black with line length 192** (`-l 192`)
- Lint: `run_flake8.bat` (ignores E402, F401, W503, E203, E501; output to `doc\flake8_report.txt`)
- Type check: `scripts\run_mypy.bat`
- Build sdist + wheel: `build.bat` (runs `python -m build`)
- Publish to PyPI: `scripts\pypi.bat` (builds, `twine check`, then `twine upload`)

## Architecture notes

The non-obvious parts live in `pref/pref.py`:

- **`_PreferenceMeta` sentinel types** (`_PreferenceMetaStr`, `_PreferenceMetaBool`):
  these wrap the bookkeeping attributes (`application_name`, `application_author`,
  `table`, `file_name`, `_pref_init`). The `__setattr__` / `__attrs_post_init__` logic
  uses `isinstance(value, _PreferenceMeta)` to decide what *not* to persist — so the
  config metadata stays out of the DB while the subclass's real preference attributes
  are written. When adding internal bookkeeping fields, give them a `_PreferenceMeta`
  type or they will be persisted as preferences.

- **`Pref` sync model**: `__attrs_post_init__` loads existing values from SQLite into
  the instance; `__setattr__` writes back to SQLite, but only after `_pref_init` is
  `True` (set at the end of init) and only when the value actually changed. `_pref_init`
  starts as a class variable and becomes an instance variable once init completes —
  this guards against DB writes during construction.

- **`PrefOrderedSet` storage trick**: ordering is stored by making the list *string*
  the SQLite key and its *index* the value, then `get()` returns
  `sorted(dict, key=dict.get)`. Consequences: duplicates collapse, and non-string
  inputs come back as strings (see `test_pref/test_pref_simple.py`).

- **Encoding**: both classes pass `encode`/`decode` identity lambdas to `SqliteDict`,
  so values are stored directly rather than pickled.

- **DB file location**: `get_sqlite_path()` uses `appdirs.user_config_dir(...)`. Default
  file name is `{application_name}.db`; a custom `file_name` must include an extension
  (asserted). Tests in `test_pref/conftest.py` delete this directory between runs via an
  autouse fixture — be aware test runs wipe the `test_pref` app config dir.

## Packaging / version

Packaging is fully declarative in `pyproject.toml` (PEP 621 + PEP 639, setuptools
backend); there is no `setup.py`. The version is **single-sourced** from
`pref/__version__.py` via `[tool.setuptools.dynamic]` (`version = {attr = ...}`), so
bump it there only — `pyproject.toml` has no hardcoded version. `__version__.py` also
holds the other metadata constants still imported at runtime by `pref/__init__.py`.
