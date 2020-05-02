Finding areas to contribute
---------------------------

Eventually, all the CPython tests should pass under x-python.  You can add
CPython tests until some of them fail, and then you've found a bug!

Tests
-----

I use pyenv as my virtual environments to run tests. I also have a GNU
Makefile to run tests so I don't have to remember the idiosyncracies
of each programming language environment. (But if *you* want to
remember this stuff that works too.

::

   make check

Underneath this is just running

::

   nosetests

If you have all Python versions supported, then you can run:

::
   make check-all

However there is a cooler version of GNU make called `remake` that
works here as well.

x-python can also use tox to run the test suite under both the various
Python versions support. Tox will create a virtualenv for each Python
verison.  Here are some useful `tox` an `nosetests` commands.

General construction::

    tox [args to tox] -- [args to nosetests]

Running only one version of Python with tox::

    tox -e py34
    tox -e py35

Running one test with tox & nosetests::

    tox -- tests.test_file:TestClass.test_name

Pass the -s flag to make nosetests not capture stdout.  Note that because of
the x-python tests' structure, this will make the test fail even if it would
otherwise pass.

::

    tox -e py34 -- -s tests.test_file:TestClass.test_name
