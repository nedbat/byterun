"""Basic tests for Byterun."""

from __future__ import print_function
from . import vmtest


class TestIt(vmtest.VmTestCase):
    def test_constant(self):
        self.assert_ok("17")

    def test_printing(self):
        self.assert_ok("print('hello')")
        self.assert_ok("a = 3; print(a+4)")

    def test_printing_in_a_function(self):
        self.assert_ok("""\
            def fn():
                print("hello")
            fn()
            print("bye")
            """)

    def test_for_loop(self):
        self.assert_ok("""\
            out = ""
            for i in range(5):
                out = out + str(i)
            print(out)
            """)

    def test_inplace_operators(self):
        self.assert_ok("""\
            text = "one"
            text += "two"
            text += "three"
            print(text)
            """)

    def test_slice(self):
        self.assert_ok("""\
            print("hello, world"[3:8])
            """)
        self.assert_ok("""\
            print("hello, world"[:8])
            """)
        self.assert_ok("""\
            print("hello, world"[3:])
            """)
        self.assert_ok("""\
            print("hello, world"[:])
            """)

    def test_slice_assignment(self):
        self.assert_ok("""\
            l = list(range(10))
            l[3:8] = ["x"]
            print(l)
            """)
        self.assert_ok("""\
            l = list(range(10))
            l[:8] = ["x"]
            print(l)
            """)
        self.assert_ok("""\
            l = list(range(10))
            l[3:] = ["x"]
            print(l)
            """)
        self.assert_ok("""\
            l = list(range(10))
            l[:] = ["x"]
            print(l)
            """)

    def test_slice_deletion(self):
        self.assert_ok("""\
            l = list(range(10))
            del l[3:8]
            print(l)
            """)
        self.assert_ok("""\
            l = list(range(10))
            del l[:8]
            print(l)
            """)
        self.assert_ok("""\
            l = list(range(10))
            del l[3:]
            print(l)
            """)
        self.assert_ok("""\
            l = list(range(10))
            del l[:]
            print(l)
            """)

    def test_building_stuff(self):
        self.assert_ok("""\
            print((1+1, 2+2, 3+3))
            """)
        self.assert_ok("""\
            print([1+1, 2+2, 3+3])
            """)
        self.assert_ok("""\
            print({1:1+1, 2:2+2, 3:3+3})
            """)

    def test_subscripting(self):
        self.assert_ok("""\
            l = list(range(10))
            print("%s %s %s" % (l[0], l[3], l[9]))
            """)
        self.assert_ok("""\
            l = list(range(10))
            l[5] = 17
            print(l)
            """)
        self.assert_ok("""\
            l = list(range(10))
            del l[5]
            print(l)
            """)

    def test_strange_sequence_ops(self):
        # from stdlib: test/test_augassign.py
        self.assert_ok("""\
            x = [1,2]
            x += [3,4]
            x *= 2

            assert x == [1, 2, 3, 4, 1, 2, 3, 4]

            x = [1, 2, 3]
            y = x
            x[1:2] *= 2
            y[1:2] += [1]

            assert x == [1, 2, 1, 2, 3]
            assert x is y
            """)

    def test_unary_operators(self):
        self.assert_ok("""\
            x = 8
            print(-x, ~x, not x)
            """)

    def test_attributes(self):
        self.assert_ok("""\
            l = lambda: 1   # Just to have an object...
            l.foo = 17
            print(hasattr(l, "foo"), l.foo)
            del l.foo
            print(hasattr(l, "foo"))
            """)

    def test_attribute_inplace_ops(self):
        self.assert_ok("""\
            l = lambda: 1   # Just to have an object...
            l.foo = 17
            l.foo -= 3
            print(l.foo)
            """)

    def test_import(self):
        self.assert_ok("""\
            import math
            print(math.pi, math.e)
            from math import sqrt
            print(sqrt(2))
            from math import *
            print(sin(2))
            """)

    def test_classes(self):
        self.assert_ok("""\
            class Thing(object):
                def __init__(self, x):
                    self.x = x
                def meth(self, y):
                    return self.x * y
            thing1 = Thing(2)
            thing2 = Thing(3)
            print(thing1.x, thing2.x)
            print(thing1.meth(4), thing2.meth(5))
            """)

    def xxxtest_calling_methods_wrong(self):    # TODO
        self.assert_ok("""\
            class Thing(object):
                def __init__(self, x):
                    self.x = x
                def meth(self, y):
                    return self.x * y
            thing1 = Thing(2)
            print(Thing.meth(14))
            """)

    def test_callback(self):
        self.assert_ok("""\
            def lcase(s):
                return s.lower()
            l = ["xyz", "ABC"]
            l.sort(key=lcase)
            print(l)
            assert l == ["ABC", "xyz"]
            """)


class TestLoops(vmtest.VmTestCase):
    def test_for(self):
        self.assert_ok("""\
            for i in range(10):
                print(i)
            print("done")
            """)

    def test_break(self):
        self.assert_ok("""\
            for i in range(10):
                print(i)
                if i == 7:
                    break
            print("done")
            """)

    def test_continue(self):
        # fun fact: this doesn't use CONTINUE_LOOP
        self.assert_ok("""\
            for i in range(10):
                if i % 3 == 0:
                    continue
                print(i)
            print("done")
            """)

    def test_continue_in_try_except(self):
        self.assert_ok("""\
            for i in range(10):
                try:
                    if i % 3 == 0:
                        continue
                    print(i)
                except ValueError:
                    pass
            print("done")
            """)

    def test_continue_in_try_finally(self):
        self.assert_ok("""\
            for i in range(10):
                try:
                    if i % 3 == 0:
                        continue
                    print(i)
                finally:
                    print(".")
            print("done")
            """)
