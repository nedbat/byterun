#!/usr/bin/env python

from distutils.core import setup

from __pkginfo__ import (
    author,
    author_email,
    entry_points,
    install_requires,
    long_description,
    classifiers,
    short_desc,
    VERSION,
    url,
)

setup(
    name="x-python",
    version=VERSION,
    author=author,
    author_email = author_email,
    classifiers = classifiers,
    description = short_desc,
    entry_points = entry_points,
    long_description = long_description,
    long_description_content_type = "text/x-rst",
    packages = ["xpython"],
    install_requires = install_requires,
    url=url,
)
