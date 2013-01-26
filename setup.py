#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Byterun',
    version='1.0',
    description='Pure-Python Python bytecode execution',
    author='Ned Batchelder',
    author_email='ned@nedbatchelder.com',
    url='http://github.com/nedbat/byterun',
    packages=['byterun'],
    install_requires=['six'],
    )
