@echo off
pushd %~dp0
python ..\devtools.py %*
popd
@echo on