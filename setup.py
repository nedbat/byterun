#!/usr/bin/env python

from distutils.core import setup

setup(
    name='xpython',
    version='1.0.0',
    description='Pure-Python Python bytecode execution',
    author='Rocky Bernstein, Ned Batchelder, Paul Swartz, Allison Kaptur and others',
    author_email='rb@dustyfeet.com',
    url='http://github.com/rocky/xpython',
    packages=['xpython'],
    entry_points = {"console_scripts": ["xpython=xpython.__main__:main"]},
    install_requires=["six", "xdis"],
    )
