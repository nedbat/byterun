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
