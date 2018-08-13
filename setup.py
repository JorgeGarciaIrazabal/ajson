# -*- coding: utf-8 -*-

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
try:
    with open(path.join(here, 'README.rm')) as f:
        long_description = f.read()
except:
    long_description = 'ajson'

setup(
    name='ajson',
    version='0.1.0',

    description='simple serializer based on annotations',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/JorgeGarciaIrazabal/ajson.git',

    author='Jorge Garcia Irazabal',
    author_email='jorge.girazabal@gmail.com',

    # Choose your license
    license='GNU Version 3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU Version 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='json serializer annotation',
    packages=find_packages(exclude="_static"),
    install_requires=[],
    test_suite="tests",
)