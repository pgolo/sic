import sys
import os
from distutils.core import setup
from Cython.Build import cythonize

src = [
    'src/tokenizer.py'
]

setup(ext_modules=cythonize(src, compiler_directives={'language_level': '3'}, build_dir='cythonized'))
