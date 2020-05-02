1.0.1 2020-05-02 Segundo de mayo
================================

A One oh release - you know what that means.

There have been numerous changes since byterun.

Probably of most interest is probably support for newer Pythons - 3.4 and some 3.5.  3.5 is still a little weak. Using routines from [xdis](https://github.com/rocky/python-xdis) we added support for wordcode (when we get around to 3.6+) and `EXTENDED_ARGS` which is more prevelant when wordcodes are in use, since an operand size is only one byte without the "extended arg" prefix.

Since we are using `xdis`, we have the ability to read and parse bytecode files from a version of Python different from the one running. Making use of this, `xpython` can accept a bytecode file in addition to accepting Python source code.

We also added support for Python 2.6, 2.5 and 3.2. Since the `x-python` doesn't run before Python 2.7, bytecode for 2.5 and 2.6 must be supplied for those versions.

The code has been reorganized to allow support for more bytecode and to be able to scale testing to a much greater extent. (I will say that the tests that were byterun were generally pretty good for the kinds of things it tests).

The level of verbosity on `nosetest -s` has been reduced by removing the disassembly listing by default. If you want a disassembly listing, consider `pydisasm` from the `xdis` package. This works because I've pulled out many of the Python test programs from strings in the tests to individual files. This makes it much easier to debug individual problems with those tests. And it makes the test files much shorter, at the expense of more files in a test directory. However I consider that good. If the test file is a real Python file then when you edit your editor will better understand what's in the string, and you can compile it and get lint on it.  Oh, and it makes it easier to write comments describing more about what's up with the test.

Some of the bugs in `MAKE_FUNCTION` have been fixed. (It is expect that these would appear since Python function signatures are complicated the internal have changed numerous times between releases.

Some command options have now change. Of note is `-v` is now `--debug-level`, `-d` which takes an integer parameter which specifies the level of verbosity. `-d1` gives a trace of instructions while `-d2` includes the block and evaluation stack. In general I'll try to follow the Python command options, and `-d`, not `-v` is what CPython uses.

(The packaging in 1.0.0 got botched, hence we start with 1.0.1)
