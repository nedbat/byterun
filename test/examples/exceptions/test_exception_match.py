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

try:
    assert 0, "msg"
except AssertionError as e:
    assert e.args[0] == "msg"
else:
    assert False,"AssertionError not raised by assert 0"

# Bug in 2.7 was not setting traceback error, "e" == AssertError()
# in byteop RAISE_VARARGS 1
try:
    assert False
except AssertionError as e:
    assert len(e.args) == 0
else:
    assert False, "AssertionError not raised by 'assert False'"
