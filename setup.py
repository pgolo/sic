from distutils.core import setup

ext_modules = None
with open('README.md', mode='r', encoding='utf8') as f:
    long_description = f.read()

try:
    from Cython.Build import cythonize
    ext_modules = cythonize(['sic/core.py'], compiler_directives={'language_level': '3'})
except ModuleNotFoundError:
    pass
finally:
    setup(
        name='sic',
        version='1.0.2',
        description='Utility for string normalization',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/pgolo/sic',
        author='Pavel Golovatenko-Abramov',
        author_email='p.golovatenko@gmail.com',
        packages=['sic'],
        ext_modules=ext_modules,
        package_data={'sic': ['core.c', 'core.pxd', 'tokenizer.greek.xml', 'tokenizer.standard.xml', 'tokenizer.western.xml']},
        include_package_data=True,
        license='MIT',
        platforms=['any'],
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        python_requires='>=3.6'
    )
