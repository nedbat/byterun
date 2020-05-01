author='Rocky Bernstein, Ned Batchelder, Paul Swartz, Allison Kaptur and others',
author_email='rb@dustyfeet.com',
entry_points = {"console_scripts": ["xpython=xpython.__main__:main"]}
install_requires=["six", "xdis", "click"],
short_desc = "Python cross-version byte-code interpeter"
url='http://github.com/rocky/xpython'

classifiers = [
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
]
import os.path as osp


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()


def read(*rnames):
    return open(osp.join(srcdir, *rnames)).read()


# Get info from files; set: long_description and VERSION
long_description = read("README.rst") + "\n"
exec(read("xpython/version.py"))
