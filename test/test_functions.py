"""Test functions, function, function signatures, etc."""

from __future__ import print_function

try:
    import vmtest
except ImportError:
    from . import vmtest

from xdis import PYTHON_VERSION

class TestFunctions(vmtest.VmTestCase):

    def test_no_builtins(self):
        self.self_checking()

    def test_calling_function_with_args_kwargs(self):
        self.self_checking()

    def test_different_globals_may_have_different_builtins(self):
        self.do_one()

    def test_wraps(self):
        self.self_checking()

    def test_partial_with_kwargs(self):
        self.self_checking()

    def test_recursion(self):
        self.self_checking()

    def test_partial(self):
        self.self_checking()

    if 3.0 <= PYTHON_VERSION:
        def test_function_calls(self):
            self.self_checking()

    # test_pos_args has function syntax added in 3.3
    if PYTHON_VERSION >= 3.3:
        def test_pos_args(self):
            self.self_checking()

        # "yield from" and bytecode YIELD_FROM added in 3.3
        def test_yield_from_tuple(self):
            self.self_checking()

    if PYTHON_VERSION >= 3.6:
        print("Test not gone over yet for >= 3.6")
    else:

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

        def test_nested_names(self):
            self.assert_ok("""\
                def one():
                    x = 1
                    def two():
                        x = 2
                        print(x)
                    two()
                    print(x)
                one()
                """)

        def test_defining_functions_with_args_kwargs(self):
            self.do_one()

        def test_defining_functions_with_empty_args_kwargs(self):
            self.assert_ok("""\
                def fn(*args):
                    print("args is %r" % (args,))
                fn()
                """)
            self.assert_ok("""\
                def fn(**kwargs):
                    print("kwargs is %r" % (kwargs,))
                fn()
                """)
            self.assert_ok("""\
                def fn(*args, **kwargs):
                    print("args is %r, kwargs is %r" % (args, kwargs))
                fn()
                """)


class TestClosures(vmtest.VmTestCase):
    def test_closures(self):
        self.self_checking()

    def test_closure_vars_from_static_parent(self):
        self.self_checking()

    # Has function-call syntax that is only valid for 3.5+
    if PYTHON_VERSION >= 3.5:
        def test_call_ex_kw(self):
            self.self_checking()

class TestGenerators(vmtest.VmTestCase):
    def test_first(self):
        self.assert_ok("""\
            def two():
                yield 1
                yield 2
            for i in two():
                print(i)
            """)

    def test_partial_generator(self):
        self.assert_ok("""\
            from _functools import partial

            def f(a,b):
                num = a+b
                while num:
                    yield num
                    num -= 1

            f2 = partial(f, 2)
            three = f2(1)
            assert list(three) == [3,2,1]
            """)

    def test_yield_multiple_values(self):
        self.assert_ok("""\
            def triples():
                yield 1, 2, 3
                yield 4, 5, 6

            for a, b, c in triples():
                print(a, b, c)
            """)

    def test_simple_generator(self):
        self.assert_ok("""\
            g = (x for x in [0,1,2])
            print(list(g))
            """)

    def test_generator_from_generator(self):
        self.assert_ok("""\
            g = (x*x for x in range(5))
            h = (y+1 for y in g)
            print(list(h))
            """)

    def test_generator_from_generator2(self):
        self.assert_ok("""\
            class Thing(object):
                RESOURCES = ('abc', 'def')
                def get_abc(self):
                    return "ABC"
                def get_def(self):
                    return "DEF"
                def resource_info(self):
                    for name in self.RESOURCES:
                        get_name = 'get_' + name
                        yield name, getattr(self, get_name)

                def boom(self):
                    #d = list((name, get()) for name, get in self.resource_info())
                    d = [(name, get()) for name, get in self.resource_info()]
                    return d

            print(Thing().boom())
            """)

    if PYTHON_VERSION >= 3.3:
        # yield from starts in 3.3
        def test_yield_from(self):
            self.assert_ok("""\
                def main():
                    x = outer()
                    next(x)
                    y = x.send("Hello, World")
                    print(y)

                def outer():
                    yield from inner()

                def inner():
                    y = yield
                    yield y

                main()
                """)

        def test_distinguish_iterators_and_generators(self):
            self.assert_ok("""\
                class Foo(object):
                    def __iter__(self):
                        return FooIter()

                class FooIter(object):
                    def __init__(self):
                        self.state = 0

                    def __next__(self):
                        if self.state >= 10:
                            raise StopIteration
                        self.state += 1
                        return self.state

                    def send(self, n):
                        print("sending")

                def outer():
                    yield from Foo()

                for x in outer():
                    print(x)
                """)

        def test_nested_yield_from(self):
            self.assert_ok("""\
                def main():
                    x = outer()
                    next(x)
                    y = x.send("Hello, World")
                    print(y)

                def outer():
                    yield from middle()

                def middle():
                    yield from inner()

                def inner():
                    y = yield
                    yield y

                main()
                """)

        def test_return_from_generator(self):
            self.assert_ok("""\
                def gen():
                    yield 1
                    return 2

                x = gen()
                while True:
                    try:
                        print(next(x))
                    except StopIteration as e:
                        print(e.value)
                        break
            """)

        def test_return_from_generator_with_yield_from(self):
            self.assert_ok("""\
                def returner():
                    if False:
                        yield
                    return 1

                def main():
                    y = yield from returner()
                    print(y)

                list(main())
            """)

if __name__ == "__main__":
    # import unittest
    # unittest.main()

    t = TestFunctions("test_functions")
    t.test_functions()
