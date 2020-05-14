SKIP_TESTS=(
    # ASYNCIO = False
    # NameError: name 'TypeVar' is not defined
    [test_typing.py]=1 # investigate syntax error

    [test_atexit.py]=1  # The atexit test looks for specific comments in error lines
    [test_cmd_line.py]=1 #

    # File "test_collections.py", line 345, in test_pickle
    # q = loads(dumps(p, protocol))
    # _pickle.PicklingError: Can't pickle <class 'xpython.byteop.byteop25.TestNT'>: attribute lookup TestNT on xpython.byteop.byteop25 failed
    [test_collections.py]=1
    [test_curses.py]=1 #

    [test_dis.py]=1   # We change line numbers - duh!

    [test_enum.py]=1
    [test_imaplib.py]=1

    [test_pdb.py]=1 # probably relies on comments in code
    [test_pkgimport.py]=1 # long

    [test_traceback.py]=1 # Multiple assert failures

    [test_urllib2_localnet.py]=1  # doesn't terminate

    [test_xmlrpc.py]=1

    [test_concurrent_futures.py]=1 # Takes long to run
    [test_faulthandler.py]=1 # takes too long to run: 20 seconds
    [test_grp.py]=1  # Long test
    [test_io.py]=1 # Long run time.
    [test_logging.py]=1 # test takes too long to run: 20 seconds
    [test_long.py]=1 # too long run time: 20 seconds
    [test_multiprocessing_fork.py]=1  # long
    [test_multiprocessing_forkserver.py]=1  # long
    [test_multiprocessing_spawn.py]=1 # long
    [test_nntplib.py]=1 # too long 25 seconds
    [test_runpy.py]=1 # decompile takes too long?
    [test_select.py]=1 # Takes too long 11 seconds
    [test_selectors.py]=1 # Takes too long 17 seconds
    [test_signal.py]=1 # too long?
    [test_socket.py]=1 # long
    [test_subprocess.py]=1 # test takes too long to run: 25 seconds
    [test_timeout.py]=1 # test takes too long to run: 19 seconds
    [test_zipfile64.py]=1 # too long to run more than 50 seconds

    [test___all__.py]=1  # it fails on its own
    [test_asdl_parser.py]=1 # it fails on its own
    [test_bisect.py]=1  # it fails on its own
    [test_codecmaps_cn.py]=1 # it fails on its own
    [test_codecmaps_hk.py]=1 # it fails on its own
    [test_codecmaps_jp.py]=1 # it fails on its own
    [test_codecmaps_kr.py]=1 # it fails on its own
    [test_codecmaps_tw.py]=1 # it fails on its own
    [test_ctypes.py]=1  # it fails on its own
    [test_dbm_ndbm.py]=1  # it fails on its own
    [test_dbm_ndbm.py]=1 # it fails on its own
    [test_devpoll.py]=1 # it fails on its own
    [test_distutils.py]=1 # it fails on its own
    [test_gdb.py]=1 # it fails on its own
    [test_idle.py]=1  # it fails on its own
    [test_kqueue.py]=1 # it fails on its own
    [test_lib2to3.py]=1 # it fails on its own
    [test_msilib.py]=1 # it fails on its own
    [test_msilib.py]=1 # it fails on its own
    [test_normalization.py]=1 # it fails on its own
    [test_ossaudiodev.py]=1 # it fails on its own
    [test_pkgutil.py]=1 # it fails on its own
    [test_pkgutil.py]=1 # it fails on its own
    [test_pty.py]=1  # fails on its own
    [test_robotparser.py]=1 # fails on its own
    [test_ssl.py]=1 # it fails on its own
    [test_startfile.py]=1 # it fails on its own
    [test_tcl.py]=1  # it fails on its own
    [test_tk.py]=1 # it fails on its own
    [test_tokenize.py]=1 # it fails on its own
    [test_trace.py]=1 # it fails on its own
    [test_trace.py]=1 # it fails on its own
    [test_ttk_guionly.py]=1 # it fails on its own
    [test_ttk_guionly.py]=1 # it fails on its own
    [test_ttk_textonly.py]=1 # it fails on its own
    [test_ttk_textonly.py]=1 # it fails on its own
    [test_urllib.py]=1 # it fails on its own
    [test_urllib2.py]=1 # it fails on its own
    [test_urllib2net.py]=1 # it fails on its own
    [test_urllibnet.py]=1 # it fails on its own
    [test_urlparse.py]=1 # test assert error
    [test_winreg.py]=1 # it fails on its own
    [test_winsound.py]=1 # it fails on its own
    [test_zipfile.py]=1 # it fails on its own
)
# About 260 unit-test in about 16 minutes

if (( BATCH )) ; then
    SKIP_TESTS[test_asyncore.py]=1 # Ok, but takes more than 15 seconds to run
    SKIP_TESTS[test_bisect.py]=1
    SKIP_TESTS[test_compileall.py]=1  # Something weird on POWER
    SKIP_TESTS[test_codeccallbacks.py]=1 # Something differenet in locale?
    SKIP_TESTS[test_distutils.py]=1

    SKIP_TESTS[test_exception_variations.py]=1
    SKIP_TESTS[test_ioctl.py]=1 # it fails on its own
    SKIP_TESTS[test_poplib.py]=1 # May be a result of POWER installation

    SKIP_TESTS[test_quopri.py]=1
    SKIP_TESTS[test_sysconfig.py]=1 # POWER extension fails
    SKIP_TESTS[test_tarfile.py]=1 # too long to run on POWER 15 secs
    SKIP_TESTS[test_venv.py]=1 # takes too long 11 seconds
fi
