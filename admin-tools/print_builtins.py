#
"""
List Python builtins for a given version.

Set the python version before running this
"""
import sys

try:
    # In Py 2.x, the builtins were in __builtin__
    BUILTINS = sys.modules["__builtin__"]
except KeyError:
    # In Py 3.x, they're in builtins
    BUILTINS = sys.modules["builtins"]

print(
    '''"""
A list of builtins for %s
"""
builtins = set(
    ['''
    % (sys.version,)
)


for name in sorted(BUILTINS.__dict__.keys()):
    print('        "%s",' % name)
print(
    """    ]
)"""
)
