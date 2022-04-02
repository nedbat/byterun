"""
Compatiability of built-in functions between different Python versions
"""


def make_compatible_builtins(BUILTINS, target_python):
    if "cmp" not in BUILTINS.__dict__:
        BUILTINS.__dict__["cmp"] = cmp


def cmp(self, other):
    if self < other:
        return -1
    elif self > other:
        return 1
    else:
        return 0
