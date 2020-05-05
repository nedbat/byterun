# This tests the use of the "global" statement.

# This program has the simplest of subroutine calls
# so generally it is a good program to try
# when expanding the interpreter such as for a new
# Python version.

"""This program is self-checking!"""

global xyz
xyz=2106

def abc():
    global xyz
    xyz+=1
    assert xyz == 2107, "Midst failed"

assert xyz == 2106, "Pre failed"
abc()
assert xyz == 2107, "Post failed"
