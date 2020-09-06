# sic

[![pypi][pypi-img]][pypi-url]

[pypi-img]: https://img.shields.io/pypi/v/sic?style=plastic
[pypi-url]: https://pypi.org/project/sic/

###### _(Latin)_ so, thus, such, in such a way, in this way
###### _(English)_ spelling is correct

`sic` is a module for string normalization. Given a string, it separates
sequences of alphabetical, numeric, and punctuation characters, as well
as performs more complex transformation (i.e. separates or replaces specific
words or individual symbols). It comes with set of default normalization rules
to transliterate and tokenize greek letters and replace accented characters
with their base form. It also allows using custom normalization configurations.

Basic usage:

```python
import sic

builder = sic.Builder()
machine = builder.build_normalizer()
x = machine.normalize('abc123xyzalphabetagammag')
print(x)
```

The output will be:

```bash
abc 123 xyz alpha beta gamma g
```

## Installation

- `sic` is designed to work in Python 3 environment.
- `sic` only needs Python Standard Library (no other packages).

To get wheel for Windows (Python >= 3.6) or source code package for Linux:

```bash
pip install sic
```

To get source code package regardless the OS:

```bash
pip install sic --no-binary sic
```

Wheels and .tar.gz can also be downloaded from the project's repository.

Wheels contain binaries compiled from cythonized code. Source code package is
pure Python. Cythonized version performs better on short strings, while non-
cythonized version performs better on long strings, so one may be preferred
over another depending on usage scenario. The benchmark is below.

| STRING LENGTH | REPEATS | VERSION | MEAN TIME (s) |
|:-------------:|:-------:|:-------:|:-------------:|
| 71            | 10000   | .tar.gz | 1.4           |
| 71            | 10000   | wheel   | 0.4           |
| 710000        | 1       | .tar.gz | 2.2           |
| 710000        | 1       | wheel   | 14.0          |
|||||||||||||||||||||||||||||||||||||||||||||||||||||

## Tokenization configs

`sic` implements tokenization, i.e. it splits a given string into tokens and
processes those tokens according to the rules specified in a configuration
file. Basic tokenization includes separating groups of alphabetical, numerical,
and punctuation characters within a string, thus turning them into separate
words (for future reference, we'll call such words `tokens`). For instance,
`abc-123` will be transformed into `abc - 123`, having tokens `abc`, `-`, and
`123`.

What happens next to initially tokenized string must be defined using XML in
configuration file(s). Entry point to default tokenizer applied to a string is
`sic/tokenizer.standard.xml`.

Below is the template and description for tokenizer config.

```xml
<!-- tokenizer.config.xml -->
<!--
  This is the description of config file for tokenizer.
  General structure:
  <tokenizer>
  +-<import>
  +-...
  +-<import>
  +-<setting>
  +-...
  +-<setting>
  +-<split>
  +-...
  +-<split>
  +-<token>
  +-...
  +-<token>
  +-<character>
  +-...
  +-<character>
-->

<?xml version="1.0" encoding="UTF-8"?>

<!-- There must be single root element, and it must be <tokenizer>: -->
<tokenizer name="$name">
<!-- $name: string label for this tokenizer -->
  
  <!--
    Direct children of <tokenizer> are <import>, <setting>, <split>,
      <token>, and/or <character> elements (there can be zero to many
      declarations of any of those)
  -->

  <!-- <import> elements point at other tokenizer configs to merge with -->
  <import file="$file" />
  <!-- $file: path to file with another tokenizer config -->

  <!-- <setting> elements define high-level tokenizer settings -->
  <setting name="$name" value="$value" />
  <!--
    Names and value requirements for /tokenizer/setting elements:
    $name="cs": $value="0"|"1" (if "1", this tokenizer will be case-sensitive)
    $name="bypass": $value="0"|"1" (if "1", this tokenizer will do nothing,
      regardless the rest content of this file)
  -->

  <!--
    <split> elements define substrings that should be separated from text as
      tokens
  -->
  <split where="$where" value="$value" />
  <!--
    $where="l"|"r"|"m" ("l" for left, "r" for right, "m" for middle)
    $value: string that will be handled as token when it's either in the
      beginning of word ($where="l"), at the end of word ($where="r"), or in
      the middle ($where="m")
  -->

  <!--
    <token> elements define tokens that should be replaced with other tokens
      (or with nothing => removed)
  -->
  <token to="$to" from="$from" />
  <!--
    $to: string that should replace the token specified in $from
    $from: string that is the token to be replaced by another string specified
      in $to
  -->

  <!--
    <character> elements define single characters that should be replaced with
      other single characters
  -->
  <character to="$to" from="$from" />
  <!--
    $to: character that should replace the another character specified in $from
    $from: character that should be replaced by another character specified in
      $to
  -->

</tokenizer>
```

Below are descriptions and examples of tokenizer config elements.

|    ELEMENT    |            ATTRIBUTES             |                                                              DESCRIPTION                                                              |                               EXAMPLE                                |
|:-------------:|:---------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------:|
| `<import>`    | file="path/to/another/config.xml" | Import tokenization rules from another tokenizer config.                                                                              |                                                                      |
| `<setting>`   | name="bypass" value="?"           | If present and value="1", all tokenization rules are ignored, as if there was no tokenization at all (left for debug purposes).       |                                                                      |
| `<setting>`   | name="cs" value="?"               | If value="1", string is processed case-sensitively; if value="0" - case-insensitively; if not present, tokenizer is case-insensitive. |                                                                      |
| `<split>`     | where="l" value="?"               | Separates token specified in `value` from **left** part of a bigger token.                                                            | where="l" value="kappa": `nf kappab` --> `nf kappa b`                |
| `<split>`     | where="m" value="?"               | Separates token specified in `value` when it is found in the **middle** of a bigger token.                                            | where="m" value="kappa": `nfkappab` --> `nf kappa b`                 |
| `<split>`     | where="r" value="?"               | Separates token specified in `value` from **right** part of a bigger token.                                                           | where="r" value="gamma": `ifngamma` --> `ifn gamma`                  |
| `<token>`     | to="?" from="?"                   | Replaces token specified in `to` with another token specified in `from`.                                                              | to="protein" from="gene": `nf kappa b gene` --> `nf kappa b protein` |
| `<character>` | to="?" from="?"                   | Replaces character specified in `to` with another character specified in `from`.                                                      | to="e" from="ë": `citroën` --> `citroen`                             |
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

Attribute `where` of `<split>` element may have any combination of `l`, `m`, or
`r` literals if the specified substring is required to be separated in different
places of a bigger string. So, instead of three different elements

```xml
<split where="l" value="word">
<split where="m" value="word">
<split where="r" value="word">
```

using the following single one

```xml
<split where="lmr" value="word">
```

will achieve the same result.

Transformation is applied in the following order:

1. Replacing characters
2. Splitting tokens
3. Replacing tokens

When splitting tokens, longer ones shadow shorter ones.

## Usage

```python
import sic
```

For detailed description of all function and methods, see comments in the
source code.

### Class `Builder`

**Function** `Builder.build_normalizer()` reads tokenization config,
instantiates `Normalizer` class that would perform tokenization according to
rules specified in a given config, and returns this `Normalizer` class
instance.

| ARGUMENT | TYPE | DEFAULT |              DESCRIPTION              |
|:--------:|:----:|:-------:|:-------------------------------------:|
| filename | str  | None    | Path to tokenizer configuration file. |
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

```python
# create Builder object
builder = sic.Builder()

# create Normalizer object with default set of rules
machine = builder.build_normalizer()

# create Normalizer object with custom set of rules
machine = builder.build_normalizer('/path/to/config.xml')
```

### Class `Normalizer`

**Function** `Normalizer.normalize()` performs string normalization according
to the rules ingested at the time of class initialization, and returns
normalized string.

|     ARGUMENT      | TYPE | DEFAULT |            DESCRIPTION             |
|:-----------------:|:----:|:-------:|:----------------------------------:|
| source_string     | str  |   n/a   | String to normalize.               |
| word_separator    | str  |   ' '   | Word delimiter (single character). |
| normalizer_option | int  |    0    | Mode of post-processing.           |
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

`word_separator`: Specified character will be considered a boundary between
tokens. The default value is `' '` (space) which seems reasonable choice for
natural language. However any character can be specified, which might be more
useful in certain context.

`normalizer_option`: The value can be either one of `0`, `1`, or `2` and
controls the way tokenized string is post-processed:

| VALUE |                             MODE                              |
|:-----:|:-------------------------------------------------------------:|
|   0   | No post-processing.                                           |
|   1   | Rearrange tokens in alphabetical order.                       |
|   2   | Rearrange tokens in alphabetical order and remove duplicates. |
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

**Property** `Normalizer.result` retains the result of last call for
`Normalizer.normalize` function as dict object with the following keys:

|     KEY      |   VALUE TYPE    |                 DESCRIPTION                          |
|:------------:|:---------------:|:----------------------------------------------------:|
| 'original'   | str             | Original string value that was processed.            |
| 'normalized' | str             | Returned normalized string value.                    |
| 'map'        | list(int)       | Map between original and normalized strings.         |
| 'r_map'      | list(list(int)) | Reverse map between original and normalized strings. |
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

`Normalizer.result['map']`: Not only `Normalizer.normalize()` generates
normalized string out of originally provided, it also tries to map character
indexes in normalized string back on those in the original one. This map is
represented as list of integers where item index is character position in
normalized string and item value is character position in original string. This
is only valid when `normalizer_option` argument for `Normalizer.normalize()`
call has been set to 0.

`Normalizer.result['r_map']`: Reverse map between character locations in
original string and its normalized reflection (item index is character position
in original string; item value is list [`x`, `y`] where `x` and `y` are
respectively lowest and highest indexes of mapped characted in normalized
string.

```python
# using default word_separator and normalizer_option
x = machine.normalize('alpha-2-macroglobulin-p')
print(x) # 'alpha - 2 - macroglobulin - p'
print(machine.result)
"""
{
  'original': 'alpha-2-macroglobulin-p',
  'normalized': 'alpha - 2 - macroglobulin - p',
  'map': [
    0, 1, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 22, 22
  ],
  'r_map: [
    [0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 6], [7, 8], [9, 10], [11, 12], [13, 13], [14, 14], [15, 15], [16, 16], [17, 17], [18, 18], [19, 19], [20, 20], [21, 21], [22, 22], [23, 23], [24, 24], [25, 26], [27, 28]
  ]
}
"""

# using custom word separator
x = machine.normalize('alpha-2-macroglobulin-p', word_separator='|')
print(x) # 'alpha|-|2|-|macroglobulin|-|p'

# using normalizer_option=1
x = machine.normalize('alpha-2-macroglobulin-p', normalizer_option=1)
print(x) # '- - - 2 alpha macroglobulin p'

# using normalizer_option=2
x = machine.normalize('alpha-2-macroglobulin-p', normalizer_option=2)
print(x) # '- 2 alpha macroglobulin p'
```
