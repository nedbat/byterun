"""Basic Python interpreter tests for x-python."""
from __future__ import print_function

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis.version_info import PYTHON3, PYTHON_VERSION_TRIPLE, version_tuple_to_str

PY2 = not PYTHON3


class TestBasic(vmtest.VmTestCase):
    def test_attribute_access(self):
        self.self_checking()

        self.assert_ok(
            """\
            class Thing2(object):
                z = 17
                def __init__(self):
                    self.x = 23
            t = Thing2()
            print(t.xyzzy)
            """,
            raises=AttributeError,
        )

    def test_bound_method_on_falsy_objects(self):
        self.self_checking()

    def test_building_stuff(self):
        self.self_checking()

    def test_callback(self):
        self.self_checking()

    def test_calling_methods_wrong(self):
        self.self_checking()

    def test_comparisons(self):
        self.self_checking()

    def test_comprehensions(self):
        self.self_checking()

    def test_generator_expression(self):
        self.self_checking()

    def test_inplace_operators(self):
        self.self_checking()

    def test_import(self):
        self.self_checking()

    def test_slice(self):
        self.self_checking()

    def test_slice_stmts(self):
        self.self_checking()

    def test_subscripting(self):
        self.self_checking()

    if PYTHON_VERSION_TRIPLE in ((3, 9),):
        print("Test not gone over yet for %s" % vresion_tuple_to_str())
    else:

        if PY2:

            def test_inplace_division2(self):
                self.assert_ok(
                    """\
                    x, y = 24, 3
                    x /= y
                    assert x == 8 and y == 3
                    assert isinstance(x, int)
                    x /= y
                    assert x == 2 and y == 3
                    assert isinstance(x, int)
                    """
                )

        elif PYTHON3:

            def test_inplace_division3(self):
                self.assert_ok(
                    """\
                    x, y = 24, 3
                    x /= y
                    assert x == 8.0 and y == 3
                    assert isinstance(x, float)
                    x /= y
                    assert x == (8.0/3.0) and y == 3
                    assert isinstance(x, float)
                    """
                )

        def test_strange_sequence_ops(self):
            # from stdlib: test/test_augassign.py
            self.do_one()

        def test_unary_operators(self):
            self.assert_ok(
                """\
                x = 8
                print(-x, ~x, not x)
                """
            )

        def test_attribute_inplace_ops(self):
            self.assert_ok(
                """\
                l = lambda: 1   # Just to have an object...
                l.foo = 17
                l.foo -= 3
                print(l.foo)
                """
            )

        def test_deleting_names(self):
            self.assert_ok(
                """\
                g = 17
                assert g == 17
                del g
                g
                """,
                raises=NameError,
            )

        def test_deleting_local_names(self):
            self.assert_ok(
                """\
                def f():
                    l = 23
                    assert l == 23
                    del l
                    l
                f()
                """,
                raises=NameError,
            )

        def test_classes(self):
            self.assert_ok(
                """\
                class Thing(object):
                    def __init__(self, x):
                        self.x = x
                    def meth(self, y):
                        return self.x * y
                thing1 = Thing(2)
                thing2 = Thing(3)
                print(thing1.x, thing2.x)
                print(thing1.meth(4), thing2.meth(5))
                """
            )

        def test_calling_subclass_methods(self):
            self.assert_ok(
                """\
                class Thing(object):
                    def foo(self):
                        return 17

                class SubThing(Thing):
                    pass

                st = SubThing()
                print(st.foo())
                """
            )

        def test_subclass_attribute(self):
            self.assert_ok(
                """\
                class Thing(object):
                    def __init__(self):
                        self.foo = 17
                class SubThing(Thing):
                    pass
                st = SubThing()
                print(st.foo)
                """
            )

        def test_subclass_attributes_not_shared(self):
            self.assert_ok(
                """\
                class Thing(object):
                    foo = 17
                class SubThing(Thing):
                    foo = 25
                st = SubThing()
                t = Thing()
                assert st.foo == 25
                assert t.foo == 17
                """
            )

        def test_object_attrs_not_shared_with_class(self):
            self.assert_ok(
                """\
                class Thing(object):
                    pass
                t = Thing()
                t.foo = 1
                Thing.foo""",
                raises=AttributeError,
            )

        def test_data_descriptors_precede_instance_attributes(self):
            self.assert_ok(
                """\
                class Foo(object):
                    pass
                f = Foo()
                f.des = 3
                class Descr(object):
                    def __get__(self, obj, cls=None):
                        return 2
                    def __set__(self, obj, val):
                        raise NotImplementedError
                Foo.des = Descr()
                assert f.des == 2
                """
            )

        def test_instance_attrs_precede_non_data_descriptors(self):
            self.assert_ok(
                """\
                class Foo(object):
                    pass
                f = Foo()
                f.des = 3
                class Descr(object):
                    def __get__(self, obj, cls=None):
                        return 2
                Foo.des = Descr()
                assert f.des == 3
                """
            )

        def test_subclass_attributes_dynamic(self):
            self.assert_ok(
                """\
                class Foo(object):
                    pass
                class Bar(Foo):
                    pass
                b = Bar()
                Foo.baz = 3
                assert b.baz == 3
                """
            )

        def test_staticmethods(self):
            self.assert_ok(
                """\
                class Thing(object):
                    @staticmethod
                    def smeth(x):
                        print(x)
                    @classmethod
                    def cmeth(cls, x):
                        print(x)

                Thing.smeth(1492)
                Thing.cmeth(1776)
                """
            )

        def test_unbound_methods(self):
            self.assert_ok(
                """\
                class Thing(object):
                    def meth(self, x):
                        print(x)
                m = Thing.meth
                m(Thing(), 1815)
                """
            )

        def test_bound_methods(self):
            self.assert_ok(
                """\
                class Thing(object):
                    def meth(self, x):
                        print(x)
                t = Thing()
                m = t.meth
                m(1815)
                """
            )

        def test_unpacking(self):
            self.assert_ok(
                """\
                a, b, c = (1, 2, 3)
                assert a == 1
                assert b == 2
                assert c == 3
                """
            )

        if PY2:

            def test_exec_statement(self):
                self.assert_ok(
                    """\
                    g = {}
                    exec "a = 11" in g, g
                    assert g['a'] == 11
                    """
                )

        elif PYTHON3:

            def test_exec_statement(self):
                self.assert_ok(
                    """\
                    g = {}
                    exec("a = 11", g, g)
                    assert g['a'] == 11
                    """
                )

        def test_multiple_classes(self):
            # Making classes used to mix together all the class-scoped values
            # across classes.  This test would fail because A.__init__ would be
            # over-written with B.__init__, and A(1, 2, 3) would complain about
            # too many arguments.
            self.assert_ok(
                """\
                class A(object):
                    def __init__(self, a, b, c):
                        self.sum = a + b + c

                class B(object):
                    def __init__(self, x):
                        self.x = x

                a = A(1, 2, 3)
                b = B(7)
                print(a.sum)
                print(b.x)
                """
            )

    if PY2:

        class TestPrinting(vmtest.VmTestCase):
            def test_printing(self):
                self.assert_ok("print 'hello'")
                self.assert_ok("a = 3; print a+4")
                self.assert_ok(
                    """
                    print 'hi', 17, u'bye', 23,
                    print "", "\t", "the end"
                    """
                )

            def test_printing_in_a_function(self):
                self.assert_ok(
                    """\
                    def fn():
                        print "hello"
                    fn()
                    print "bye"
                    """
                )

            def test_printing_to_a_file(self):
                self.assert_ok(
                    """\
                    import sys
                    print >>sys.stdout, 'hello', 'there'
                    """
                )

    class TestLoops(vmtest.VmTestCase):
        def test_break(self):
            self.assert_ok(
                """\
                for i in range(10):
                    print(i)
                    if i == 7:
                        break
                print("done")
                """
            )

        def test_continue(self):
            # fun fact: this doesn't use CONTINUE_LOOP
            self.assert_ok(
                """\
                for i in range(10):
                    if i % 3 == 0:
                        continue
                    print(i)
                print("done")
                """
            )

        def test_continue_in_try_except(self):
            self.assert_ok(
                """\
                for i in range(10):
                    try:
                        if i % 3 == 0:
                            continue
                        print(i)
                    except ValueError:
                        pass
                print("done")
                """
            )

        def test_continue_in_try_finally(self):
            self.assert_ok(
                """\
                for i in range(10):
                    try:
                        if i % 3 == 0:
                            continue
                        print(i)
                    finally:
                        print(".")
                print("done")
                """
            )


if __name__ == "__main__":
    # import unittest
    # unittest.main()

    t = TestBasic("test_building_stuff")
    # t.test_decorator()
    # t = TestComparisons("test_in")
    # t.test_in()
    # t = TestComparisons("test_greater")
    # t.test_greater()
