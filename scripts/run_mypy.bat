pushd .
cd ..
call venv\Scripts\activate.bat 
mypy -m pref
mypy -m test_pref
call deactivate
popd
