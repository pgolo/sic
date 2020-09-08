# This directory

## buildso.sh

Compiles `SO` file (used for testing), places it in `../../dist`.

## buildtargz.sh

Builds `.tar.gz` package, places it in `../../dist`.
Usage: `buildtargz.sh path/to/python`

## buildwheel.sh

Builds wheels, places them in `../../dist`.
Usage: `buildwheel.sh path1/to/python path2/to/python`

## testing.sh

Builds `PYD` with `buildpyd.sh`, runs unit tests and performance assessment.

## vscode.sh

Provides some settings for VS Code IDE.
