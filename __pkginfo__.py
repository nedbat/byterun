import sys

author = "Rocky Bernstein, Ned Batchelder, Paul Swartz, Allison Kaptur and others"
author_email = "rb@dustyfeet.com"
entry_points = {"console_scripts": ["xpython=xpython.__main__:main"]}

# Python-version | package | last-version |
# -----------------------------------------
# 3.2            | click   | 4.0          |
# 3.2            | pip     | 8.1.2        |
# 3.3            | pip     | 10.0.1       |
# 3.4            | pip     | 19.1.1       |

import os.path as osp


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


exec(read("xpython/version.py"))

PYTHON_VERSION = sys.version_info[0] + (sys.version_info[1] / 10.0)
IS_PYPY = "__pypy__" in sys.builtin_module_names

supported_versions = SUPPORTED_PYPY if IS_PYPY else SUPPORTED_PYTHON
mess = "PYPY 2.7, 3.2, 3.5 and 3.6" if IS_PYPY else "CPython 2.7, 3.2 .. 3.7"

if PYTHON_VERSION not in supported_versions:
    python = "PyPy " if IS_PYPY else "C"
    print("We only support %s; you have %sPython %s" % (mess, python, PYTHON_VERSION))
    raise Exception(mess)

if 3.0 <= PYTHON_VERSION <= 3.2:
    click_version = "<= 4.0"
else:
    click_version = ""

install_requires = (["six", "xdis >= 5.0.1, < 5.1.0", "click%s" % click_version],)

py_modules = None
short_desc = "Python cross-version byte-code interpeter"
url = "http://github.com/rocky/xpython"

classifiers = [
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]

# Get/set VERSION and long_description from files
long_description = read("README.rst") + "\n"
exec(read("xpython/version.py"))
