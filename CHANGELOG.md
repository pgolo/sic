# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## sic 1.3

### [1.3.3] - 2021-09-17

#### Changed

- Fixed bug causing incorrect normalization when replacement tokens can be tokenized themselves

### [1.3.2] - 2021-01-21

#### Changed

- Improved logical reasoning to resolve conflicting instructions

### [1.3.1] - 2020-12-08

#### Changed

- Updated logic with respect to spelling correction

### [1.3.0] - 2020-11-30

#### Added

- Support for transitivity in tokenization rules
- Option to identify tokens but don't add word separators to resulting string

## sic 1.2

### [1.2.0] - 2020-11-09

#### Added

- Tokenization rules can be added to a compiled model

## sic 1.1

### [1.1.0] - 2020-10-31

#### Added

- Implicit instantiation of core classes
- Classes and function for ad hoc creation of tokenization config
- Methods to save (pickle) and load (unpickle) compiled Normalizer instance
- Wheel for Python 3.9

## sic 1.0

### [1.0.6] - 2020-09-10

#### Changed

- Fixed bug with replacing substring that is not a token

### [1.0.5] - 2020-09-08

#### Changed

- Normalizer.data is now exposed as a property
- Updated documentation, added performance benchmarks
- Installable package is either pure Python or wheel with precompiled Cython

### [1.0.4] - 2020-09-03

#### Added

- Normalizer.result['r_map'] attribute
- Scripts to build wheels

### [1.0.3] - 2020-07-30

#### Added

- Normalizer.data attribute is now exposed and can be accessed directly

### [1.0.2] - 2020-06-12

#### Added

- Added README.md in released package

### [1.0.1] - 2020-06-12

#### Added

- Module is cythonized at the time of installation

### [1.0.0] - 2020-06-12

#### Added

- Configurable string normalization module
