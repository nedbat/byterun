# Python 3.3+
#
# This file is derived from 02_pos_args in the uncompyle6 distribution.
#
# From Python 3.3.6 hmac.py
# Problem was getting wrong placement of positional args.
# In 3.6+ parameter handling changes

"""This program is self-checking!"""

digest_cons = lambda d=b'': 5

# Handle single keyword-only arg
x = lambda *, d=0: d
assert x(d=1) == 1
assert x() == 0
