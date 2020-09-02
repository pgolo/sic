@echo off
rem Usage:
rem buildwheel.bat path\to\python36 path\to\python37 path\to\python38

set RUNDIR=%cd%
set MYDIR=%~dp0
set ROOT=%MYDIR%\..\..
set REQUIREMENTS=%ROOT%\requirements.txt
set ENV=%ROOT%\.env.build

:BUILD
if (%1)==() (exit)
if not exist "%1" (echo "%1": Python not found && shift && goto BUILD)
cd "%ROOT%"
virtualenv -p "%1" "%ENV%"
"%ENV%"\Scripts\python -m pip install --no-cache-dir -r "%REQUIREMENTS%"
"%ENV%"\Scripts\python "%ROOT%"\setup.py bdist_wheel
rmdir /S /Q "%ENV%"
shift
goto BUILD
