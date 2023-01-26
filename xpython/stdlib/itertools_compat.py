"""
Replacement for built-in itertools.

This version needs to be compatibie across all versions of Python
"""
import sys
import itertools

for name, value in itertools.__dict__.items():
    locals()[name] = value

if sys.version_info >= (3, 0):
    izip_longest = itertools.zip_longest
else:
    zip_longest = itertools.izip_longest
