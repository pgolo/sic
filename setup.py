from distutils.core import setup

ext_modules = None

try:
    from Cython.Build import cythonize
    ext_modules = cythonize('sic/core.py')
except ModuleNotFoundError:
    pass
finally:
    setup(
        name='sic',
        version='1.0.0',
        description='Utility for string normalization',
        url='https://github.com/pgolo/sic',
        author='Pavel Golovatenko-Abramov',
        author_email='p.golovatenko@gmail.com',
        packages=['sic'],
        ext_modules=ext_modules,
        license='MIT',
        include_package_data=True
    )
