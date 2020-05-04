# Test provided by Darius
#
# https://github.com/nedbat/byterun/pull/20/commits/70727da1e5c6f98075b2eeecc597cb81b43e7c4f
# for issue https://github.com/nedbat/byterun/issues/17
def f(xs):
    return lambda: xs[0]


def g(h):
    xs = 5
    lambda: xs
    return h()


assert g(f([42])) == 42
