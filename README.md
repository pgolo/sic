# sic

###### _(Latin)_ so, thus, such, in such a way, in this way
###### _(English)_ spelling is correct

`sic` is a module for string normalization. Given a string, it separates
sequences of alphabetical, numeric, and punctuation characters, as well
as performs more complex transformation (i.e. separates or replaces specific
words or individual symbols). It comes with set of default normalization rules
to transliterate and tokenize greek letters and replace accented characters
with their base form. It also allows using custom normalization configuration.

Basic usage:

```python
import sic

builder = sic.Builder()
machine = builder.build_tokenizer()
x = machine.tokenize('abc123xyzalphabetagammag')
print(x)
```

The output will be:

```bash
abc 123 xyz alpha beta gamma g
```

## Installation

```bash
pip install sic
```

- `sic` is designed to work in Python 3 environment.
- `sic` only needs Python Standard Library (no other packages).
- Although `sic` leaves very little footprint, it is recommended that in
  production environment, `Cython` is installed at the time of `sic`
  installation. Then the module will be cythonized and will work much faster.
  `Cython` is not required for `sic` to run, once `sic` is installed.

## Usage

```python
import sic
```

### Class `Builder`

Reads normalization config and instantiates `Tokenizer` class.

```python
# create Tokenizer object with default set of rules
machine = sic.Builder.build_tokenizer()

# create Tokenizer object with custom set of rules
machine = sic.Builder.build_tokenizer('/path/to/config.xml')
```

### Class `Tokenizer`

Performs string normalization.

```python
machine.tokenize('Master Yoda is normalizing NFkappaB')
machine.tokenize('Master Yoda is normalizing NFkappaB', tokenizer_option=1)
machine.tokenize('Master Yoda is normalizing NFkappaB', tokenizer_option=2)
```

## Normalization configs

sss
