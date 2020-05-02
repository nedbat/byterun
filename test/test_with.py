"""Test the "with" statement for x-python."""

from __future__ import print_function

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis import PYTHON_VERSION

class TestWithStatement(vmtest.VmTestCase):

    def test_simple_context_manager(self):
        self.do_one()

    if PYTHON_VERSION < 3.5:
        def test_raise_in_context_manager(self):
            self.do_one()

        def test_suppressed_raise_in_context_manager(self):
            self.assert_ok("""\
                class SuppressingContext(object):
                    def __enter__(self):
                        l.append('i')
                        return self

                    def __exit__(self, exc_type, exc_val, exc_tb):
                        assert exc_type is ValueError, \\
                            "Expected ValueError: %r" % exc_type
                        l.append('o')
                        return True

                l = []
                try:
                    with SuppressingContext():
                        l.append('w')
                        raise ValueError("Boo!")
                    l.append('e')
                except ValueError:
                    l.append('x')
                l.append('r')
                s = ''.join(l)
                print("Look: %r" % s)
                assert s == "iwoer"
                """)

    def test_return_in_with(self):
        self.assert_ok("""\
            class NullContext(object):
                def __enter__(self):
                    l.append('i')
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    l.append('o')
                    return False

            l = []
            def use_with(val):
                with NullContext():
                    l.append('w')
                    return val
                l.append('e')

            assert use_with(23) == 23
            l.append('r')
            s = ''.join(l)
            print("Look: %r" % s)
            assert s == "iwor"
            """)

    def test_continue_in_with(self):
        self.do_one()

    if PYTHON_VERSION < 3.5:
        def test_break_in_with(self):
            self.assert_ok("""\
                class NullContext(object):
                    def __enter__(self):
                        l.append('i')
                        return self

                    def __exit__(self, exc_type, exc_val, exc_tb):
                        l.append('o')
                        return False

                l = []
                for i in range(3):
                    with NullContext():
                        l.append('w')
                        if i % 2:
                           break
                        l.append('z')
                    l.append('e')

                l.append('r')
                s = ''.join(l)
                print("Look: %r" % s)
                assert s == "iwzoeiwor"
                """)

        def test_raise_in_with(self):
            self.assert_ok("""\
                class NullContext(object):
                    def __enter__(self):
                        l.append('i')
                        return self

                    def __exit__(self, exc_type, exc_val, exc_tb):
                        l.append('o')
                        return False

                l = []
                try:
                    with NullContext():
                        l.append('w')
                        raise ValueError("oops")
                        l.append('z')
                    l.append('e')
                except ValueError as e:
                    assert str(e) == "oops"
                    l.append('x')
                l.append('r')
                s = ''.join(l)
                print("Look: %r" % s)
                assert s == "iwoxr", "What!?"
                """)

    def test_at_context_manager_simplified(self):
        self.assert_ok("""\
            """)

    if PYTHON_VERSION >= 3.3:
        # FIXME - this a bug in 3.2 handling
        def test_at_context_manager_complete(self):
            self.do_one()

        # yield from is not in 3.2-
        def test_generator_with_context_manager(self):
            self.do_one()
