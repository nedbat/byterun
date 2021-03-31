"""This program is self-checking!"""

try:
    [][1]
    assert False, "Direct exception test: shouldn't be here..."
except IndexError:
    print("caught direct IndexError exception")

# Catch the exception by a parent class
try:
    [][1]
    assert False, "Parent exception test: shouldn't be here..."
except Exception:
    print("caught parent of IndexError exception")


try:
    [][1]
    assert False, "generic exception test: shouldn't be here..."
except:
    print("caught general 'except'")
