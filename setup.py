#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

setup(name="dev_bytebot",
      packages=find_packages(),
      scripts=["index.py"],
      )
