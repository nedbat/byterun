"""Things involving data, variables, and typesin x-python."""

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis.version_info import PYTHON_VERSION_TRIPLE


class TestData(vmtest.VmTestCase):
    def test_constant(self):
        self.do_one()

    def test_attributes(self):
        self.self_checking()

    def test_eval(self):
        self.self_checking()

    if (3, 5) <= PYTHON_VERSION_TRIPLE < (3, 10):
        # {**{}} is illegal before 3.5
        def test_map_unpack(self):
            self.self_checking()

    if (3, 6) <= PYTHON_VERSION_TRIPLE < (3, 10):
        # No fstrings before 3.6
        def test_fstring(self):
            self.self_checking()
