try:
    from Cython.Build import cythonize
    ext_modules = cythonize(['sic/core.py'], compiler_directives={'language_level': '3'})
except:
    pass
