"""Test exceptions."""

from __future__ import print_function
import unittest

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis.version_info import PYTHON_VERSION_TRIPLE, PYTHON3

PY2 = not PYTHON3


class TestExceptions(vmtest.VmTestCase):

    if PYTHON_VERSION_TRIPLE >= (3, 8):
        print("Test not gone over yet for >= 3.8")
    else:

        def test_exception_match(self):
            self.self_checking()

    if PYTHON_VERSION_TRIPLE < (3, 9):

        def test_catching_exceptions(self):
            self.self_checking()

    def test_raise_exception(self):
        self.assert_ok("raise Exception('oops')", raises=Exception)

    def test_raise_exception_class(self):
        self.assert_ok("raise ValueError", raises=ValueError)

    def test_coverage_issue_92(self):
        self.assert_ok("raise ValueError", raises=ValueError)

    if PYTHON_VERSION_TRIPLE >= (3, 6):
        print("Test not gone over yet for >= 3.6")
    else:
        if PY2:

            def test_raise_exception_2args(self):
                self.assert_ok("raise ValueError, 'bad'", raises=ValueError)

            def test_raise_exception_3args(self):
                self.assert_ok(
                    """\
                    from sys import exc_info
                    try:
                        raise Exception
                    except:
                        _, _, tb = exc_info()
                    raise ValueError, "message", tb
                    """,
                    raises=ValueError,
                )

        def test_raise_and_catch_exception(self):
            self.assert_ok(
                """\
                try:
                    raise ValueError("oops")
                except ValueError as e:
                    print("Caught: %s" % e)
                print("All done")
                """
            )

        if PYTHON3:

            def test_raise_exception_from(self):
                self.assert_ok("raise ValueError from NameError", raises=ValueError)

        def test_raise_and_catch_exception_in_function(self):
            self.assert_ok(
                """\
                def fn():
                    raise ValueError("oops")

                try:
                    fn()
                except ValueError as e:
                    print("Caught: %s" % e)
                print("done")
                """
            )

        def test_global_name_error(self):
            self.assert_ok("fooey", raises=NameError)
            self.assert_ok(
                """\
                try:
                    fooey
                    print("Yes fooey?")
                except NameError:
                    print("No fooey")
                """
            )

            def test_local_name_error(self):
                self.assert_ok(
                    """\
                    def fn():
                        fooey
                    fn()
                    """,
                    raises=NameError,
                )

        def test_catch_local_name_error(self):
            self.assert_ok(
                """\
                def fn():
                    try:
                        fooey
                        print("Yes fooey?")
                    except NameError:
                        print("No fooey")
                fn()
                """
            )

        # def test_reraise(self):
        #     self.assert_ok("""\
        #         def fn():
        #             try:
        #                 fooey
        #                 print("Yes fooey?")
        #             except NameError:
        #                 print("No fooey")
        #                 raise
        #         fn()
        #         """, raises=NameError)

        def test_reraise_explicit_exception(self):
            self.assert_ok(
                """\
                def fn():
                    try:
                        raise ValueError("ouch")
                    except ValueError as e:
                        print("Caught %s" % e)
                        raise
                fn()
                """,
                raises=ValueError,
            )

        def test_finally_while_throwing(self):
            self.assert_ok(
                """\
                def fn():
                    try:
                        print("About to..")
                        raise ValueError("ouch")
                    finally:
                        print("Finally")
                fn()
                print("Done")
                """,
                raises=ValueError,
            )


if __name__ == "__main__":
    unittest.main()
