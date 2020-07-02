# From 2.7.18 test_grammar.py adapted so it will run on later Pythons

# Tests EXEC_STMT on 2.7- and exec() builtin on 3.0+

"""This program is self-checking!"""
z = None
del z

exec('z=1+1\n')

if z != 2:
    assert False, "exec 'z=1+1'\n"
del z

exec('z=1+1')

# Make sure we can exec bytes as well as strings.
import sys
if sys.version_info[:2] >= (2, 5):
    if sys.version_info[:2] >= (3, 0):
        exec(bytes('# coding: cp949\na = "\xaa\xa7"\n', encoding="cp949"))
    else:
        exec(bytes('# coding: cp949\na = "\xaa\xa7"\n'))

# And one eval test...
if not ((3, 0) <= sys.version_info[:2] <= (3, 2)):
    code = u'u"\xc2\xa4"\n'
    assert eval(code) == u'\xc2\xa4'
