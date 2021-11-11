"""Test Python statements."""
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

try:
    import vmtest
except ImportError:
    from . import vmtest

if PYTHON_VERSION_TRIPLE[:2] in ((3, 10),):
    print("Test not gone over yet for %s" % version_tuple_to_str())

    class TestStmts(vmtest.VmTestCase):
        def test_for_loop(self):
            pass


else:

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
