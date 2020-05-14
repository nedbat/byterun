SKIP_TESTS=(

    # File "test_enum.py", line 75, in test_pickle_dump_load
    # assertion(loads(dumps(source, protocol=protocol)), target)
    # _pickle.PicklingError: Can't pickle <enum 'Answer'>: attribute lookup Answer on xpython.byteop.byteop25 failed
    #  FAIL: test_dir_on_item (__main__.TestEnum)
    # Traceback (most recent call last):
    # File "test_enum.py", line 161, in test_dir_on_item
    # set(['__class__', '__doc__', '__module__', 'name', 'value']),
    # AssertionError: Items in the first set but not the second:
    # 'version'
    [test_enum.py]=1

    # test_warnings.py:106: UserWarning: FilterTests.test_ignore_after_default
    # self.module.warn(message, UserWarning)
    # .....test_warnings.py:106: UserWarning: FilterTests.test_ignore_after_default
    # self.module.warn(message, UserWarning)
    # ................E..................
    # ERROR: test_missing_filename_main_with_argv (__main__.PyWarnTests)
    # line_string = line.decode('utf-8')
    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xee in position 0: invalid continuation byte
    [test_warnings.py]=1


    # _pickle.PicklingError: Can't pickle <class 'xpython.byteop.byteop25.TestNT'>: attribute lookup TestNT on xpython.byteop.byteop25 failed
    [test_collections.py]=1

    [test_curses.py]=1 # Investigate

    [test_dis.py]=1   # 2 test assert failures

    [test_multiprocessing_fork.py]=1 # doesn't terminate
    [test_multiprocessing_forkserver.py]=1 # doesn't terminate
    [test_multiprocessing_main_handling.py]=1  # doesn't terminate
    [test_multiprocessing_spawn.py]=1 # doesn't terminate

    # File "python3.4/unittest/case.py", line 137, in __init__
    # _BaseTestCaseContext.__init__(self, test_case)
    # RuntimeError: maximum recursion depth exceeded
    [test_sys.py]=1

    [test_tcl.py]=1 # May be implementation specific. On POWER though it fails

    [test_traceback.py]=1 # introspects on code

    [test_buffer.py]=1  # test takes too long to run: 16 seconds
    [test_cmd_line.py]=1 # takes too long to run
    [test_concurrent_futures.py]=1  # too long?
    [test_decimal.py]=1  # Takes too long to run: 25 seconds
    [test_faulthandler.py]=1 # takes too long to run: 20 seconds
    [test_fork1.py]=1 # too long
    [test_io.py]=1 # Too long to run
    [test_ioctl.py]=1 # it fails on its own
    [test_logging.py]=1 # Too long to run
    [test_nntplib.py]=1 # too long to run
    [test_pkgimport.py]=1 # long
    [test_poll.py]=1 # Too long to run: 11 seconds
    [test_runpy.py]=1 # Too long:
    [test_select.py]=1 # Too long: 11 seconds
    [test_selectors.py]=1  # Too long: 11 seconds
    [test_signal.py]=1 # Too long: 22 seconds
    [test_socket.py]=1 # long 25 seconds
    [test_socketserver.py]=1 # long 25 seconds
    [test_subprocess.py]=1 # Too long
    [test_threading.py]=1 # Too long
    [test_threadsignals.py]=1 # Too long to run: 12 seconds
    [test_timeout.py]=1 # Too long to run: 19 seconds

    [test___all__.py]=1  # it fails on its own
    [test_ctypes.py]=1  # it fails on its own
    [test_dbm_gnu.py]=1   # fails on its own
    [test_dbm_ndbm.py]=1  # it fails on its own
    [test_devpoll.py]=1 # it fails on its own
    [test_distutils.py]=1 # it fails on its own
    [test_doctest.py]=1  # it fails on its own
    [test_gdb.py]=1 # it fails on its own
    [test_httplib.py]=1 # it fails on its own
    [test_idle.py]=1  # it fails on its own
    [test_import.py]=1 # it fails on its own
    [test_kqueue.py]=1 # it fails on its own
    [test_lib2to3.py]=1 # it fails on its own
    [test_msilib.py]=1 # it fails on its own
    [test_ossaudiodev.py]=1 # it fails on its own
    [test_pkgutil.py]=1 # it fails on its own
    [test_readline.py]=1 # it fails on its own
    [test_ssl.py]=1 # it fails on its own
    [test_startfile.py]=1 # it fails on its own
    [test_tk.py]=1 # it fails on its own
    [test_tokenize.py]=1 # it fails on its own
    [test_trace.py]=1 # it fails on its own
    [test_ttk_guionly.py]=1 # it fails on its own
    [test_ttk_textonly.py]=1 # it fails on its own
    [test_winreg.py]=1 # it fails on its own
    [test_winsound.py]=1 # it fails on its own


)
# Ran 314 unit-test files, 59 errors; Elapsed time: 7 minutes

if (( batch )) ; then
    # Fails in crontab environment?
    # Figure out what's up here
    SKIP_TESTS[test_exception_variations.py]=1
    SKIP_TESTS[test_mailbox.py]=1 # Takes to long on POWER; over 15 secs
    SKIP_TESTS[test_quopri.py]=1
fi
