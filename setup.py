#!/usr/bin/env python

import os

from distutils.core import setup
from setuptools import find_packages

setup(name='canape',
      description='a tvshow downloader',
      url='https://github.com/nduhamel/canape',
      packages = find_packages(),
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Operating System :: OS Independent'
      ]
     )
