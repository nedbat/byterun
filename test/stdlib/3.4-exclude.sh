SKIP_TESTS=(
    [test_decimal.py]=1  # Takes too long to run: 25 seconds
    [test_buffer.py]=1  # test takes too long to run: 16 seconds

    [test___all__.py]=1  # it fails on its own
    [test_atexit.py]=1  # The atexit test looks for specific comments in error lines

    [test_cmd_line.py]=1 # takes too long to run
    [test_concurrent_futures.py]=1  # too long?

    [test_ctypes.py]=1 # it fails on its own
    [test_curses.py]=1 # Investigate

    [test_dbm_gnu.py]=1   # fails on its own
    [test_devpoll.py]=1 # it fails on its own
    [test_dis.py]=1   #
    [test_distutils.py]=1 # it fails on its own
    [test_doctest.py]=1  # it fails on its own

    [test_enum.py]=1 #
    [test_exceptions.py]=1

    [test_faulthandler.py]=1
    [test_fork1.py]=1 # too long

    [test_gdb.py]=1 # it fails on its own

    [test_httplib.py]=1 # it fails on its own

    [test_import.py]=1 # it fails on its own
    [test_io.py]=1 # Too long to run
    [test_ioctl.py]=1 # it fails on its own

    [test_logging.py]=1 # Too long to run

    [test_modulefinder.py]=1  # test assertion error
    [test_multiprocessing_fork.py]=1 # doesn't terminate
    [test_multiprocessing_forkserver.py]=1 # doesn't terminate
    [test_multiprocessing_main_handling.py]=1  # doesn't terminate
    [test_multiprocessing_spawn.py]=1 # doesn't terminate

    [test_nntplib.py]=1 # too long to run

    [test_peepholer.py]=1 # control flow?
    [test_pep352.py]=1 # test assert failures
    [test_pickle.py]=1 # test assert failures
    [test_pkgimport.py]=1 # long
    [test_poll.py]=1 # Too long to run: 11 seconds
    [test_pydoc.py]=1 # test assertion failures

    [test_runpy.py]=1 # Too long:

    [test_select.py]=1 # Too long: 11 seconds
    [test_selectors.py]=1  # Too long: 11 seconds
    [test_signal.py]=1 # Too long: 22 seconds
    [test_sndhdr.py]=1
    [test_socket.py]=1 # long 25 seconds
    [test_socketserver.py]=1 # long 25 seconds
    [test_subprocess.py]=1 # Too long
    [test_symtable.py]=1 # Investigate bad output
    [test_sys_settrace.py]=1 # test assert failures

    [test_tcl.py]=1 # May be implementation specific. On POWER though it fails
    [test_threading.py]=1 # Too long
    [test_threadsignals.py]=1 # Too long to run: 12 seconds
    [test_timeout.py]=1 # Too long to run: 19 seconds
    [test_traceback.py]=1 # introspects on code

    [test_urllib2net.py]=1 # Doesn't terminate

    [test_zipfile64.py]=1
    [test_zlib.py]=1
)
# 304 unit-test file in about 20 minutes

if (( batch )) ; then
    # Fails in crontab environment?
    # Figure out what's up here
    SKIP_TESTS[test_exception_variations.py]=1
    SKIP_TESTS[test_mailbox.py]=1 # Takes to long on POWER; over 15 secs
    SKIP_TESTS[test_quopri.py]=1
fi
