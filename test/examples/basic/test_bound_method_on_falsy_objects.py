# See https://github.com/nedbat/byterun/pull/33:
#
# Because instances of Falsy are falsy, `func.im_self` in
# call_function() of xpython/pyvm2.ptreated them as nonexistent and
# did not add the self parameter to the argument list.
#
# The problem was exhibited on Python 2.7.
class Falsy(object):
    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def do_stuff(self):
        # See the HitchHiker's guide
        return 42


assert Falsy().do_stuff() == 42
