#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'wlpac'
DESCRIPTION = 'Warped Linear Prediction Audio Codec'
URL = 'https://github.com/sevagh/warped-linear-prediction'
EMAIL = 'sevag.hanssian@gmail.com'
AUTHOR = 'Sevag Hanssian'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    py_modules=['wlpac'],
    entry_points={
        'console_scripts': [
            'wlpac_encode=wlpac.cli:encode',
            'wlpac_decode=wlpac.cli:decode',
            'wlpac_compare=wlpac.cli:compare',
        ],
    },
    include_package_data=True,
    license='MIT',
)
