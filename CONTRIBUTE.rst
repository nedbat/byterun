Finding areas to contribute
---------------------------

Eventually, all the CPython tests should pass under byterun.  You can add
CPython tests until some of them fail, and then you've found a bug!

Tests
-----

Byterun uses tox to run the test suite under both Python 2.7 and Python 3.3.
Tox will create a virtualenv for each Python verison.  Here are some useful tox
+ nosetests commands.

General construction::

    tox [args to tox] -- [args to nosetests]

Running only one version of Python with tox::

    tox -e py27
    tox -e py33

Running one test with tox & nosetests::

    tox -- tests.test_file:TestClass.test_name

Pass the -s flag to make nosetests not capture stdout.  Note that because of
the byterun tests' structure, this will make the test fail even if it would
otherwise pass.

::

    tox -e py33 -- -s tests.test_file:TestClass.test_name
