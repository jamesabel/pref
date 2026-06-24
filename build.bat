rmdir /S /Q dist 2>nul
rmdir /S /Q build 2>nul
rmdir /S /Q pref.egg-info 2>nul
call venv\Scripts\activate.bat
python -m build
call deactivate
