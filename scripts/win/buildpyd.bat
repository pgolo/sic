@echo off
set RUNDIR=%cd%
set ROOT=%~dp0..\..
set ENV=.env.37
set SRC=%ROOT%\sic
set DIST=%ROOT%\dist
set TEST=%ROOT%\test
cd %ROOT%
rmdir /S /Q %ROOT%\build
rmdir /S /Q %ROOT%\cythonized
if not exist %DIST%\nul mkdir %DIST%
call %ROOT%\%ENV%\Scripts\python %TEST%\compile.py build_ext --inplace
move /Y %SRC%\*.pyd %DIST%\
cd %RUNDIR%