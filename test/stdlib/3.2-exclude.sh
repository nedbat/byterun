SKIP_TESTS=(
    # Expect to delve to to the intricacies of classes here
    [test_abc.py]=1

    # File x-python/xpython/pyobj.py", line 237, in __init__
    # assert f_back.cells, "f_back.cells: %r" % (f_back.cells,)
    [test_array.py]=1

    # TypeError: argument to reversed() must be a sequence
    [test_asynchat.py]=1

    [test_asyncore.py]=1
    [test_atexit.py]=1  # The atexit test starting at 3.3 looks for specific comments in error lines

    # investigate: Received value insufficiently close to expected value.
    # Expected: complex(0.0, 0.0)
    # Received value insufficiently close to expected value.
    [test_cmath.py]=1

    [test_cmd_line.py]=1 # too long?
    [test_concurrent_futures.py]=1  # too long?
    [test_datetimetester.py]=1
    [test_decimal.py]=1
    [test_descr.py]=1
    [test_dictcomps.py]=1 # FIXME: semantic error: actual = {k:v for k in }
    [test_doctest.py]=1 # test failures
    [test_dis.py]=1   # We change line numbers - duh!
    [test_exceptions.py]=1 # parse error

    [test_modulefinder.py]=1 # test failures
    [test_multiprocessing.py]=1 # test takes too long to run: 35 seconds

    [test_peepholer.py]=1
    [test_pep352.py]=1

    [test_quopri.py]=1 # TypeError: Can't convert 'bytes' object to str implicitly

    [test_runpy.py]=1

    [test_ssl.py]=1 # too installation specific
    [test_startfile.py]=1 # fails on its own
    [test_subprocess.py]=1  # fails on its own
    [test_tcl.py]=1 # it fails on its own
    [test_tk.py]=1 # it fails on its own
    [test_traceback.py]=1 # it fails on its own
    [test_zipfile64.py]=1 # Too long to run

)

if (( BATCH )) ; then
    # Fails in crontab environment?
    # Figure out what's up here
    SKIP_TESTS[test_exception_variations.py]=1
    SKIP_TESTS[test_quopri.py]=1
fi
