#!/usr/bin/env python

from distutils.core import setup

from setuptools import setup, find_packages
from __pkginfo__ import (
    VERSION,
    author,
    author_email,
    classifiers,
    entry_points,
    install_requires,
    long_description,
    py_modules,
    short_desc,
    url,
)

setup(
    name="x-python",
    version=VERSION,
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    description=short_desc,
    entry_points=entry_points,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=find_packages(),
    py_modules = py_modules,
    install_requires=install_requires,
    url=url
)
