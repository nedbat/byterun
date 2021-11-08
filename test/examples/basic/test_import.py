# Adapted from the a test in byterun's test_basic.py.

"""This program is self-checking!"""

# fmt: off
import math

assert math.pi == 3.141592653589793
assert math.e == 2.718281828459045
from math import sin
from math import *  # noqa

assert sin(2) == 0.9092974268256817

# We were having problems with import of os.path finding the right module
# We were finding os.posix instead of os. This checks that.
import os.path as osp
assert osp.join("/tmp", "foo") == "/tmp/foo"
