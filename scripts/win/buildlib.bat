@echo off
set RUNDIR=%cd%
set ROOT=%~dp0..\..
set ENV=.env.37
cd %ROOT%
rmdir /S /Q %ROOT%\build
rmdir /S /Q %ROOT%\cythonized
if not exist %ROOT%\dist\nul mkdir %ROOT%\dist
call %ROOT%\%ENV%\Scripts\python %ROOT%\src\compile.py build_ext --inplace
move /Y .\*.pyd %ROOT%\dist
cd %RUNDIR%
