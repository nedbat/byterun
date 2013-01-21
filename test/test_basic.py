import vmtest

class TestIt(vmtest.VmTestCase):
    def test_constant(self):
        self.assert_ok("17")

    def test_printing(self):
        self.assert_ok("print 'hello'")
        self.assert_ok("a = 3; print a+4")

    def test_printing_in_a_function(self):
        self.assert_ok("""\
            def fn():
                print "hello"
            fn()
            print "bye"
            """)

    def test_recursive_functions(self):
        self.assert_ok("""\
            def pow(b, e):
                if e == 0:
                    return 1
                else:
                    return b*pow(b, e-1)
            print "2**6 is %d" % pow(2, 6)
            """)

    def test_catching_exceptions(self):
        # Catch the exception precisely
        self.assert_ok("""\
            try:
                [][1]
                print "Shouldn't be here..."
            except IndexError:
                print "caught it!"
            """)
        # Catch the exception by a parent class
        self.assert_ok("""\
            try:
                [][1]
                print "Shouldn't be here..."
            except Exception:
                print "caught it!"
            """)
        # Catch all exceptions
        self.assert_ok("""\
            try:
                [][1]
                print "Shouldn't be here..."
            except:
                print "caught it!"
            """)

    def test_raise_exception(self):
        self.assert_ok("raise Exception('oops')")

    def test_raise_and_catch_exception(self):
        self.assert_ok("""\
            try:
                raise ValueError("oops")
            except ValueError, e:
                print "Caught: %s" % e
            print "All done"
            """)

    def test_raise_and_catch_exception_in_function(self):
        self.assert_ok("""\
            def fn():
                raise ValueError("oops")

            try:
                fn()
            except ValueError, e:
                print "Caught: %s" % e
            print "done"
            """)

    def test_global_name_error(self):
        self.assert_ok("fooey")
        self.assert_ok("""\
            try:
                fooey
                print "Yes fooey?"
            except NameError:
                print "No fooey"
            """)

    def test_local_name_error(self):
        self.assert_ok("""\
            def fn():
                fooey
            fn()
            """)

    def test_catch_local_name_error(self):
        self.assert_ok("""\
            def fn():
                try:
                    fooey
                    print "Yes fooey?"
                except NameError:
                    print "No fooey"
            fn()
            """)

    def test_for_loop(self):
        self.assert_ok("""\
            out = ""
            for i in range(5):
                out = out + str(i)
            print out
            """)

    def test_inplace_operators(self):
        self.assert_ok("""\
            text = "one"
            text += "two"
            text += "three"
            print text
            """)

    def test_slice(self):
        self.assert_ok("""\
            print "hello, world"[3:8]
            """)
        self.assert_ok("""\
            print "hello, world"[:8]
            """)
        self.assert_ok("""\
            print "hello, world"[3:]
            """)
        self.assert_ok("""\
            print "hello, world"[:]
            """)

    def test_slice_assignment(self):
        self.assert_ok("""\
            l = range(10)
            l[3:8] = ["x"]
            print l
            """)
        self.assert_ok("""\
            l = range(10)
            l[:8] = ["x"]
            print l
            """)
        self.assert_ok("""\
            l = range(10)
            l[3:] = ["x"]
            print l
            """)
        self.assert_ok("""\
            l = range(10)
            l[:] = ["x"]
            print l
            """)

    def test_slice_deletion(self):
        self.assert_ok("""\
            l = range(10)
            del l[3:8]
            print l
            """)
        self.assert_ok("""\
            l = range(10)
            del l[:8]
            print l
            """)
        self.assert_ok("""\
            l = range(10)
            del l[3:]
            print l
            """)
        self.assert_ok("""\
            l = range(10)
            del l[:]
            print l
            """)

    def test_building_stuff(self):
        self.assert_ok("""\
            print (1+1, 2+2, 3+3)
            """)
        self.assert_ok("""\
            print [1+1, 2+2, 3+3]
            """)
        self.assert_ok("""\
            print {1:1+1, 2:2+2, 3:3+3}
            """)

    def test_subscripting(self):
        self.assert_ok("""\
            l = range(10)
            print "%s %s %s" % (l[0], l[3], l[9])
            """)
        self.assert_ok("""\
            l = range(10)
            l[5] = 17
            print l
            """)
        self.assert_ok("""\
            l = range(10)
            del l[5]
            print l
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
            x, s = 8, "Hello\\n"
            print -x, `s`, not x
            """)

    def test_functions(self):
        self.assert_ok("""\
            def fn(a, b=17, c="Hello", d=[]):
                d.append(99)
                print a, b, c, d
            fn(1)
            fn(2, 3)
            fn(3, c="Bye")
            fn(4, d=["What?"])
            fn(5, "b", "c")
            """)

    def test_args_kwargs_functions(self):
        self.assert_ok("""\
            def fn(a, b=17, c="Hello", d=[]):
                d.append(99)
                print a, b, c, d
            fn(6, *[77, 88])
            fn(**{'c': 23, 'a': 7})
            fn(6, *[77], **{'c': 23, 'd': [123]})
            """)

    def test_attributes(self):
        self.assert_ok("""\
            l = lambda: 1   # Just to have an object...
            l.foo = 17
            print hasattr(l, "foo"), l.foo
            del l.foo
            print hasattr(l, "foo")
            """)

    def test_attribute_inplace_ops(self):
        self.assert_ok("""\
            l = lambda: 1   # Just to have an object...
            l.foo = 17
            l.foo -= 3
            print l.foo
            """)

    def test_import(self):
        self.assert_ok("""\
            import math
            print math.pi, math.e
            from math import sqrt
            print sqrt(2)
            from math import *
            print sin(2)
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
            print thing1.x, thing2.x
            print thing1.meth(4), thing2.meth(5)
            """)

    def xxxtest_calling_methods_wrong(self):    # TODO
        self.assert_ok("""\
            class Thing(object):
                def __init__(self, x):
                    self.x = x
                def meth(self, y):
                    return self.x * y
            thing1 = Thing(2)
            print Thing.meth(14)
            """)

    def test_callback(self):
        self.assert_ok("""\
            def lcase(s):
                return s.lower()
            l = ["xyz", "ABC"]
            l.sort(key=lcase)
            print l
            assert l == ["ABC", "xyz"]
            """)

class TestClosures(vmtest.VmTestCase):
    def test_closures(self):
        self.assert_ok("""\
            def make_adder(x):
                def add(y):
                    return x+y
                return add
            a = make_adder(10)
            print a(7)
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
            print a(7)
            assert a(7) == 28
            """)

    def test_closures_in_loop(self):
        self.assert_ok("""\
            def make_fns(x):
                fns = []
                for i in range(x):
                    fns.append(lambda: i)
                return fns
            fns = make_fns(3)
            for f in fns:
                print f()
            assert fns[0]() == fns[1]() == fns[2]() == 2
            """)

    def test_closures_with_defaults(self):
        self.assert_ok("""\
            def make_adder(x, y=13, z=43):
                def add(q, r=11):
                    return x+y+z+q+r
                return add
            a = make_adder(10, 17)
            print a(7)
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
            print answer
            assert answer == 54
            """)

class TestGenerators(vmtest.VmTestCase):
    def test_first(self):
        self.assert_ok("""\
            def two():
                yield 1
                yield 2
            for i in two():
                print i
            """)


class TestLoops(vmtest.VmTestCase):
    def test_for(self):
        self.assert_ok("""\
            for i in range(10):
                print i,
            print "done"
            """)

    def test_break(self):
        self.assert_ok("""\
            for i in range(10):
                print i,
                if i == 7:
                    break
            print "done"
            """)

    def test_continue(self):
        # fun fact: this doesn't use CONTINUE_LOOP
        self.assert_ok("""\
            for i in range(10):
                if i % 3 == 0:
                    continue
                print i,
            print "done"
            """)

    def test_continue_in_try_except(self):
        self.assert_ok("""\
            for i in range(10):
                try:
                    if i % 3 == 0:
                        continue
                    print i,
                except ValueError:
                    pass
            print "done"
            """)

    def test_continue_in_try_finally(self):
        self.assert_ok("""\
            for i in range(10):
                try:
                    if i % 3 == 0:
                        continue
                    print i,
                finally:
                    print ".",
            print "done"
            """)
