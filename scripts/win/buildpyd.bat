@echo off
set RUNDIR=%cd%
set ROOT=%~dp0..\..
set ENV=.env.310
set SRC=%ROOT%\sic
set DIST=%ROOT%\bin
set TEST=%ROOT%\test
cd %ROOT%
if exist %ROOT%\build\nul rmdir /S /Q %ROOT%\build
if exist %ROOT%\cythonized\nul rmdir /S /Q %ROOT%\cythonized
if exist %DIST%\nul rmdir /S /Q %DIST%
if not exist %DIST%\nul mkdir %DIST%
call %ROOT%\%ENV%\Scripts\python %TEST%\compile.py build_ext --inplace
move /Y %SRC%\*.pyd %DIST%\
copy /Y %SRC%\__init__.py %DIST%\
copy /Y %SRC%\*.xml %DIST%\
cd %RUNDIR%
