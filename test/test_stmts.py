"""Test Python statements."""

from __future__ import print_function

try:
    import vmtest
except ImportError:
    from . import vmtest

# from xdis import PYTHON_VERSION


class TestStmts(vmtest.VmTestCase):

    def test_for_loop(self):
        self.self_checking()

    def test_while(self):
        self.self_checking()

    def test_global(self):
        self.self_checking()

    def test_exec(self):
        self.self_checking()

if __name__ == "__main__":
    # import unittest
    # unittest.main()

    t = TestStmts("test_for_loop")
    t.test_for_loop()
