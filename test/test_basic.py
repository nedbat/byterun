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

    def test_raising_exceptions(self):
        self.assert_ok("print ValueError('oops')")
        self.assert_ok("raise Exception('oops')")
        self.assert_ok("""\
            try:
                raise ValueError("oops")
            except ValueError, e:
                print "Caught: %s" % e
            """)
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
