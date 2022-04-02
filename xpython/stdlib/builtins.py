"""
Compatiability of built-in functions between different Python versions
"""
from xdis.version_info import PYTHON_VERSION_TRIPLE


def make_compatible_builtins(BUILTINS, target_python):
    if PYTHON_VERSION_TRIPLE >= (3, 0):
        if "cmp" not in BUILTINS.__dict__:
            BUILTINS.__dict__["cmp"] = cmp
        if "xrange" not in BUILTINS.__dict__:
            BUILTINS.__dict__["xrange"] = range


def cmp(self, other):
    if self < other:
        return -1
    elif self > other:
        return 1
    else:
        return 0
