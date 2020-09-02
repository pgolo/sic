@echo off
rem Usage:
rem buildtargz.bat path\to\python

set RUNDIR=%cd%
set MYDIR=%~dp0
set ROOT=%MYDIR%\..\..
set REQUIREMENTS=%ROOT%\requirements.txt
set ENV=%ROOT%\.env.build

if (%1)==() (cd %RUNDIR% && exit)
if not exist "%1" (echo "%1": Python not found && exit)
cd "%ROOT%"
virtualenv -p "%1" "%ENV%"
"%ENV%"\Scripts\python -m pip install --no-cache-dir -r "%REQUIREMENTS%"
"%ENV%"\Scripts\python "%ROOT%"\setup.py sdist
rmdir /S /Q "%ENV%"

cd %RUNDIR%
