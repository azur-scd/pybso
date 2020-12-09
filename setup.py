#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path
import pybso

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
name='pybso',
version=pybso.__version__,
packages=find_packages(include=['pybso'], exclude=['demo', ]),
description='Open Access Monitoring from a DOI corpus',
long_description = long_description,
long_description_content_type="text/markdown",
url='https://github.com/gegedenice/pybso',
author='Géraldine Geoffroy',
author_email='geraldine.geoffroy@univ-cotedazur.fr',
#include_package_data=True,
package_dir={'pybso': 'pybso'},
package_data={'pybso': ['data/sample.csv','../assets/*.png']},
install_requires=[
          'pandas','requests','plotly','urllib3',
      ],
keywords = 'baromètre science ouverte open access package Python',
classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ], 
)