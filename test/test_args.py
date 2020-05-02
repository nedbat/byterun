"""Test the Python's funky parameter argument passing in x-python."""

from __future__ import print_function

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis import PYTHON_VERSION

class TestArgs(vmtest.VmTestCase):

    if PYTHON_VERSION > 3.2:
        def test_pos_args(self):
            self.do_one()
