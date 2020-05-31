# Tests various combinations of * and ** args.
# This tests opcodes:
# CALL_FUNCTION_VAR, CALL_FUNCTION_KW, CALL_FUNCTION_VAR_KW, CALL_FUNCTION_EX,
# LOAD_METHOD, and CALL_METHOD among other opcodes

"""This program is self-checking!"""

def fn(a, b=17, c="Hello", d=[]):
    d.append(99)
    return(a, b, c, d)
assert fn(6, *[77, 88]) == (6, 77, 88, [99])
assert fn(**{'c': 23, 'a': 7}) == (7, 17, 23, [99, 99])
assert fn(6, *[77], **{'c': 23, 'd': [123]}) == (6, 77, 23, [123, 99])
