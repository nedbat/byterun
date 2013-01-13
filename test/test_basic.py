import vmtest

class TestIt(vmtest.VmTestCase):
    def test_one_liners(self):
        self.assert_ok("print 'hello'")
        self.assert_ok("a = 3; print a+4")

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
        self.assert_ok("raise Exception('oops')")

    def test_name_error(self):
        self.assert_ok("fooey")
