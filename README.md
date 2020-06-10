# sic

_(Latin)_ so, thus, such, in such a way, in this way

_(English)_ spelling is correct

`sic` is a module for string normalization. Given a string, it separates sequences of alphabetical, numeric, and punctuation characters, as well as performs more complex transformation (i.e. separates or replaces specific words or individual symbols). It comes with default normalization rules to transliterate and tokenize greek letters and replace accented characters with their base form. It can also work with custom designed normalization units.

Basic usage:

```python
import sic

builder = sic.Builder()
machine = builder.build_tokenizer()
x = machine.tokenize('abcalphabetagammad')
print(x)
```

Output will be:

```python
abc alpha beta gamma d
```

## Installation

sss

## Default normalization unit

sss

## Custom normalization units

sss

