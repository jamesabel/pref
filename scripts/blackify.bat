pushd .
cd ..
call venv\Scripts\activate.bat
python -m black -l 192 pref test_pref setup.py
call deactivate
popd
