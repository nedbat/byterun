"""Things involving data, variables, and typesin x-python."""

from __future__ import print_function

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis import PYTHON_VERSION


class TestData(vmtest.VmTestCase):

    def test_constant(self):
        self.do_one()

    def test_attributes(self):
        self.self_checking()

    def test_eval(self):
        self.self_checking()

    if PYTHON_VERSION >= 3.5:

        def test_map_unpack(self):
            self.self_checking()

    if PYTHON_VERSION >= 3.6:

        def test_fstring(self):
            self.self_checking()
