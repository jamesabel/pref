# Changelog

## 0.5.0

- `config_dir=` on `Pref`, `PrefOrderedSet` and `PrefStore` places the SQLite file
  explicitly; the default is unchanged (the per-user config directory).
- `platformdirs` replaces the unmaintained `appdirs`. Paths are the same on Windows and
  Linux; on macOS a directory already present at the 0.4 location (`~/Library/Preferences`)
  keeps being used.
- `Pref` runs an attribute's `attrs` `converter` and `validator` on every set and on every
  load, so a bad value is neither stored nor loaded; loading a stored value that no longer
  validates keeps the default and logs a warning.
- `default_config_dir(application_name, application_author)` is exported.

## 0.4.0

- Previous release (see git history).
