@echo off
set RUNDIR=%cd%
set ROOT=%~dp0..\..
set ENV=.env.37
set TEST=%ROOT%\test
cd %ROOT%
set FILES=ut_tokenizer.py performance.py
(for %%f in (%FILES%) do (
    echo Running %%f
    call %ROOT%\%ENV%\Scripts\python.exe %TEST%\%%f
))
cd %RUNDIR%
