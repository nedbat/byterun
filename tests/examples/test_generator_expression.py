x = "-".join(str(z) for z in range(5))
assert x == "0-1-2-3-4"

# From test_regr.py
# This failed a different way than the previous join when genexps were
# broken:

from textwrap import fill
x = set(['test_str'])
width = 70
indent = 4
blanks = ' ' * indent
res = fill(' '.join(str(elt) for elt in sorted(x)), width,
            initial_indent=blanks, subsequent_indent=blanks)
print(res)
