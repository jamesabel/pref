pushd .
cd ..
call build.bat
call venv\Scripts\activate.bat
twine check dist/*
twine upload dist/*
call deactivate
popd
