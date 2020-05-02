"""Basic Python interpreter tests for x-python."""
from __future__ import print_function

# These can within a major version even if the interpreter version mismatches.

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis import PYTHON3
PY2 = not PYTHON3

class TestIt(vmtest.VmTestCase):

    def test_constant(self):
        self.do_one()

    def test_decorator(self):
        self.do_one()

    def test_for(self):
        self.do_one()

    def test_for_loop(self):
        self.do_one()

    def test_globals(self):
        self.do_one()

    def test_inplace_operators(self):
        self.do_one()

    def test_slice(self):
        self.do_one()

    def test_strange_sequence_ops(self):
        # from stdlib: test/test_augassign.py
        self.do_one()


if __name__ == "__main__":
    # import unittest
    # unittest.main()

    t = TestIt("test_for_loop")
    t.test_for_loop()
    # t = TestIt("test_decorator")
    # t.test_decorator()
    # t = TestComparisons("test_in")
    # t.test_in()
    # t = TestComparisons("test_greater")
    # t.test_greater()
