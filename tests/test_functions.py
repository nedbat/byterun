"""Test functions etc, for Byterun."""

from __future__ import print_function
from . import vmtest


class TestFunctions(vmtest.VmTestCase):
    def test_functions(self):
        self.assert_ok("""\
            def fn(a, b=17, c="Hello", d=[]):
                d.append(99)
                print(a, b, c, d)
            fn(1)
            fn(2, 3)
            fn(3, c="Bye")
            fn(4, d=["What?"])
            fn(5, "b", "c")
            """)

    def test_recursion(self):
        self.assert_ok("""\
            def fact(n):
                if n <= 1:
                    return 1
                else:
                    return n * fact(n-1)
            f6 = fact(6)
            print(f6)
            assert f6 == 720
            """)

    def test_args_kwargs_functions(self):
        self.assert_ok("""\
            def fn(a, b=17, c="Hello", d=[]):
                d.append(99)
                print(a, b, c, d)
            fn(6, *[77, 88])
            fn(**{'c': 23, 'a': 7})
            fn(6, *[77], **{'c': 23, 'd': [123]})
            """)


class TestClosures(vmtest.VmTestCase):
    def test_closures(self):
        self.assert_ok("""\
            def make_adder(x):
                def add(y):
                    return x+y
                return add
            a = make_adder(10)
            print(a(7))
            assert a(7) == 17
            """)

    def test_closures_store_deref(self):
        self.assert_ok("""\
            def make_adder(x):
                z = x+1
                def add(y):
                    return x+y+z
                return add
            a = make_adder(10)
            print(a(7))
            assert a(7) == 28
            """)

    def test_closures_in_loop(self):
        self.assert_ok("""\
            def make_fns(x):
                fns = []
                for i in range(x):
                    fns.append(lambda i=i: i)
                return fns
            fns = make_fns(3)
            for f in fns:
                print(f())
            assert (fns[0](), fns[1](), fns[2]()) == (0, 1, 2)
            """)

    def test_closures_with_defaults(self):
        self.assert_ok("""\
            def make_adder(x, y=13, z=43):
                def add(q, r=11):
                    return x+y+z+q+r
                return add
            a = make_adder(10, 17)
            print(a(7))
            assert a(7) == 88
            """)

    def test_deep_closures(self):
        self.assert_ok("""\
            def f1(a):
                b = 2*a
                def f2(c):
                    d = 2*c
                    def f3(e):
                        f = 2*e
                        def f4(g):
                            h = 2*g
                            return a+b+c+d+e+f+g+h
                        return f4
                    return f3
                return f2
            answer = f1(3)(4)(5)(6)
            print(answer)
            assert answer == 54
            """)

class TestGenerators(vmtest.VmTestCase):
    def test_first(self):
        self.assert_ok("""\
            def two():
                yield 1
                yield 2
            for i in two():
                print(i)
            """)



