# This directory

## buildpyd.bat

Compiles `PYD` file (used for testing), places it in `../../dist`.

## buildtargz.bat

Builds `.tar.gz` package, places it in `../../dist`.
Usage: `buildtargz.bat path\to\python.exe`

## buildwheel.bat

Builds wheels, places them in `../../dist`.
Usage: `buildwheel.bat path1\to\python.exe path2\to\python.exe`

## testing.bat

Builds `PYD` with `buildpyd.bat`, runs unit tests and performance assessment.

## vscode.bat

Provides some settings for VS Code IDE.
