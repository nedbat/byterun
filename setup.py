#!/usr/bin/env python

from distutils.core import setup

setup(
    name='xpython',
    version='1.0',
    description='Pure-Python Python bytecode execution',
    author='Ned Batchelder',
    author_email='ned@nedbatchelder.com',
    url='http://github.com/rocky/xbyterun',
    packages=['xpython'],
    entry_points = {"console_scripts": ["xpython=xpython.__main__:main"]},
    install_requires=["six", "xdis"],
    )
