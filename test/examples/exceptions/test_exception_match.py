# Tests COMPARE_OP execption_match

# Adapted from 2.7.18 test_grammar.py

"""This program is self-checking!"""

try:
    raise RuntimeError
except RuntimeError:
    pass

# KeyboardInterrupt inherits from BaseExeption, not Exception.
# Byterun had (has?) a bug in testing against Exception in
# exception-matching.

try:
    raise KeyboardInterrupt
except KeyboardInterrupt:
    pass
