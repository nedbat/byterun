1.2.1 2020-04-20 trepan-xpy
===========================

The main thrust of this release was to make it suitable to be used from a debugger.

* There is better (but not exact) conformance of Python's `sys.settrace()` API:
   - linestarts is a frame-oriented thing, not a VM thing.
   - Store callback in `f_trace`.
* Allow supplying a callback print function, so that the client can colorize the parts of the instruction
* Add screencasts


1.2.0 2020-04-19 Primidi 1st Prairial - Alfalfa - HF
====================================================

This version adds callback hooks for tracing or debugger that will be released soon.

There is more complete (but not fully complete) Version 3.5-3.7 bytecode interpretation.
(`BUILD_TUPLE_UNPACK_WITH_CALL` implemented 3.6 `MAKE_FUNCTION` corrected.)

`build_class()` has been fixed so that it picks up class variables. This means we do better at as a cross version interpreter - that's where `build_class()` is currently used.

Via `build_class()` we can track into `__entry__()` and `__exit__()` functions of a context manager.

`frame.f_lasti` had been pointing to the instruction that might be run next rather than the one that is about to be run. While this simplified interpreter implementation, it didn't follow CPython's meaning. And when this is used from a debugger this becomes unusable.

Disassembly output has been fixed up courtesy of argument information from `xdis`. `xdis` imports have been simplified in version 4.6.0, so we require that.

Additional PyPy bytecode ops (`LOOKUP_METHOD`, `CALL_METHOD`) are supported; so you can run this from PyPy now or do cross-interpretation from the corresponding CPython bytecode.

Better conformance of Python's Frame type. Added: `__qualname__` and set `__annotation__` attributes.



1.1.0 2020-05-08 Lewis-10
=========================

Here we support up to 3.6 and 3.7 now -- we're the first on the block to support Python 3.7! PyPy versions 2.7, 3.2, 3.5, and 3.6 are also supported.

A number of bug have been squashed but others still run rampant. Some the lesser-used 3.6-3.7 and PyPy opcodes haven't been implemented. However about 300 of the tests that Python's uses to test itself pass; the same is true for other versions.

There is the usual bug fixes, and code cleanups. We do a tad better in cross-version bytecode interpretation.

Tests are getting converted to a form that is more amenable test isolation and not spewing diarrhea when there is a failure.

Although this is still very much a work in progress, we've come a very long way from where this started.


1.0.1 2020-05-02 Segundo de mayo
================================

A One oh release - you know what that means.

There have been numerous changes since byterun.

Probably of most interest is probably support for newer Pythons - 3.4 and some 3.5.  3.5 is still a little weak. Using routines from [xdis](https://github.com/rocky/python-xdis) we added support for wordcode (when we get around to 3.6+) and `EXTENDED_ARGS` which is more prevalent when wordcodes are in use, since an operand size is only one byte without the "extended arg" prefix.

Since we are using `xdis`, we have the ability to read and parse bytecode files from a version of Python different from the one running. Making use of this, `xpython` can accept a bytecode file in addition to accepting Python source code.

We also added support for Python 2.6, 2.5 and 3.2. Since the `x-python` doesn't run before Python 2.7, bytecode for 2.5 and 2.6 must be supplied for those versions.

The code has been reorganized to allow support for more bytecode and to be able to scale testing to a much greater extent. (I will say that the tests that were byterun were generally pretty good for the kinds of things it tests).

The level of verbosity on `nosetest -s` has been reduced by removing the disassembly listing by default. If you want a disassembly listing, consider `pydisasm` from the `xdis` package. This works because I've pulled out many of the Python test programs from strings in the tests to individual files. This makes it much easier to debug individual problems with those tests. And it makes the test files much shorter, at the expense of more files in a test directory. However I consider that good. If the test file is a real Python file then when you edit your editor will better understand what's in the string, and you can compile it and get lint on it.  Oh, and it makes it easier to write comments describing more about what's up with the test.

Some of the bugs in `MAKE_FUNCTION` have been fixed. (It is expect that these would appear since Python function signatures are complicated the internal have changed numerous times between releases.

Some command options have now change. Of note is `-v` is now `--debug-level`, `-d` which takes an integer parameter which specifies the level of verbosity. `-d1` gives a trace of instructions while `-d2` includes the block and evaluation stack. In general I'll try to follow the Python command options, and `-d`, not `-v` is what CPython uses.

(The packaging in 1.0.0 got botched, hence we start with 1.0.1)
