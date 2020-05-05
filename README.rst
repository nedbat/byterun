|TravisCI| |CircleCI|

x-python
--------

This is a CPython bytecode interpreter written Python.

You can use this to:

* Learn about how the internals of CPython works since this models that
* Use as a sandboxed environment for trying pieces of execution
* Have one Python program that runs multiple versions of Python bytecode.
  For a number of things you can Python 2.5 or 2.6 bytecode from inside Python 3.7;
  No need to install Python 2.5 or 2.6!
* Use in a dynamic fuzzer or in coholic execution for analysis

The sandboxed environment in a debugger I find interesting. Since
there is a separate execution, and traceback stack, inside a debugger
you can try things out in the middle of a debug session without
effecting the real execution. On the other hand if a sequence of
executions works out, it is possible to copy this (under certain
circumstances) back into CPython's execution stack.

Going the other way, I may at some point hook in `my debugger
<https://pypi.python.org/pypi/trepan3k>`_ into this interpreter and then
you'll have a conventional pdb/gdb like debugger also with the ability
to step bytecode instructions.

Another unexplored avenue implied above is mixing interpretation and
direct CPython execution. In fact, there are bugs so this happens
right now, but it will be turned into a feature. Some functions or
classes you may want to not run under a slow interpreter while others
you do want to run under the interpreter.


Status:
+++++++

Currently only Python 2.5 - 2.7, and 3.2 - 3.7 bytecode is supported.
Until there is more interest or I get support or funding, I am not
contemplating expanding to 3.8 and beyond for a while.

A shout out to `xdis <https://pypi.python.org/pypi/xdis>`_ which has
made cross version interpretation and expanding to other versions
easier.

Whereas *Byterun* was a bit loose in accepting bytecode opcodes that
is invalid for particular Python but may be valid for another;
*x-python* is more stringent. This has pros and cons. On the plus side
*Byterun* might run certain Python 3.4 bytecode because the opcode
sets are similar. However starting with Python 3.5 and beyond the
likelihood gets much less because, while the underlying opcode names
may be the same, the semantics of the operation may change
subtely. See for example
https://github.com/nedbat/byterun/issues/34.

Internally Byterun needs the kind of overhaul we have here to be able
to scale to support bytecode for more Pythons, and to be able to run
bytecode across different versions of Python. Specifically, you can't
rely on Python's `dis <https://docs.python.org/3/library/dis.html>`_
module if you expect to expect to run a bytecode other than the
bytecode that the interpreter is running.

In *x-python* there is a clear distinction between the version being
interpreted and the version of Python that is running. There is
tighter control of opcodes and an opcode's implementation is kept for
each Python version. So we'll warn early when something is
invalid. You can run 3.3 bytecode using Python 3.7 (largely).

The "largely" part is because the interpreter has always made use of
Python builtins. When a Python version running the interperter matches a
supported bytecode close enough, the interpreter can (and does) make use
interpreter internals. For example, built-in functions like `range()`
are supported this way.

Currently running 2.7 bytecode on 3.x is often not feasible since the
runtime and internal libraries used like `inspect` are too different.

Over time more of Python's internals may get added so we have better
cross-version compatability, so that is a possibility. Harder is to
run later byecode from earlier Python versions. The callenge here is
that many new features like asynchronous I/O and concurrency
primatives are not in the older versions and may not easily be
simulated. However that too is a possibility if there is interest.

Right now this program works best on Python up to 3.4 when life in
Python was much simpler. You can run many of the tests that Python uses
to test itself, and those work.  Python 3.5 is pretty good too. Python
3.6 and 3.7 is okay but needs work.


History
++++++

This is a fork of *Byterun.* which is a pure-Python implementation of
a Python bytecode execution virtual machine.  Net Batchelder started
it (based on work from Paul Swartz) to get a better understanding of
bytecodes so he could fix branch coverage bugs in coverage.py.

.. |CircleCI| image:: https://circleci.com/gh/rocky/x-python.svg?style=svg
    :target: https://circleci.com/gh/rocky/x-python
.. |TravisCI| image:: https://travis-ci.org/rocky/x-python.svg?branch=master
		 :target: https://travis-ci.org/rocky/x-python
