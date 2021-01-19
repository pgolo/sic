@echo off
call %~dp0\buildpyd.bat
set RUNDIR=%cd%
set ROOT=%~dp0..\..
set ENV=.env.37
set TEST=%ROOT%\test
rem set FILES=ut_sic.py performance.py
set FILES=ut_sic.py
cd %ROOT%
(for %%f in (%FILES%) do (
    echo Running %%f
    call %ROOT%\%ENV%\Scripts\python.exe %TEST%\%%f -b
))
cd %RUNDIR%
