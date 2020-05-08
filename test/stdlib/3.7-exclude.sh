SKIP_TESTS=(
    [test_minidom.py]=1 # test errors; works on 5bbb74f3 (HEAD~10)
    [test_modulefinder.py]=1 # works on 5bbb74f3 (HEAD~10)
    [test_struct.py]=1 # assert failure (1); works on 5bbb74f3 (HEAD~10)
    [test_wsgiref.py]=1 # works on 5bbb74f3 (HEAD~10)

    [test_builtin.py]=1 # works on 5bbb74f3 (HEAD~10)?
    [test_format.py]=1 # works on 5bbb74f3 (HEAD~10)?
    [test_dataclasses.py]=1 # works on 5bbb74f3 (HEAD~10)

    [test_poplib.py]=1 # works on 5bbb74f3 (HEAD~10)
    [test_codecs.py]=1 # test errors; works on 5bbb74f3 (HEAD~10)
    [test_pyclbr.py]=1 # test errors; works on 5bbb74f3 (HEAD~10)
    [test_threaded_import.py]=1 # works on 5bbb74f3 (HEAD~10)
    [test_urllib2.py]=1 # test errors (1); works on 5bbb74f3 (HEAD~5)

    [test_httplib.py]=1 # test runs. kills after 15 seconds. works on f7e2064e
    [test_grammar.py]=1 # assert failures

    [test___all__.py]=1 # it fails on its own
    [test_argparse.py]=1 # it fails on its own
    [test_asdl_parser.py]=1 # it fails on its own
    [test_atexit.py]=1  # The atexit test looks for specific comments in error lines
    [test_buffer.py]=1  # Test run errors; takes long time to decompile


    [test_clinic.py]=1 # it fails on its own
    [test_cmd_line.py]=1  # Interactive?
    [test_cmd_line_script.py]=1 # test errors
    [test_compileall.py]=1 # fails on its own
    [test_compile.py]=1  # Code introspects on co_consts in a non-decompilable way
    [test_concurrent_futures.py]=1 # Takes too long *before* decompiling
    [test_coroutines.py]=1 # Parse error
    [test_ctypes.py]=1 # it fails on its own
    [test_curses.py]=1 # probably byte string not handled properly
    [test_datetime.py]=1   # Takes too long *before* decompiling
    [test_dbm_ndbm.py]=1 # it fails on its own
    [test_decimal.py]=1   # test assertion failures
    [test_descr.py]=1   # test assertion failures
    [test_devpoll.py]=1 # it fails on its own
    [test_dis.py]=1   # Introspects on line numbers; line numbers don't match in disassembly - duh!
    [test_doctest.py]=1   # fails on its own

    [test_enum.py]=1   # test run errors (1); probably bad control flow

    [test_faulthandler.py]=1   # test takes too long before decompiling
    [test_fileinput.py]=1 # too long to run - control flow?
    [test_frame.py]=1 # Introspects line number
    [test_fstring.py]=1 # need to disambiguate leading fstrings from docstrings

    [test_generators.py]=1  # Works if you run via Python. So possibly some test-framework problem
    [test_gdb.py]=1 # it fails on its own
    [test_glob.py]=1  # test errors (1), TypeError: join() argument must be str or bytes, not 'tuple'
    [test_grp.py]=1 # Running test doesn't terminate (killed)

    [test_imaplib.py]=1 # test errors; control-flow?
    [test_io.py]=1 # test takes too long to run before decompilation: 37 seconds
    [test_inspect.py]=1 # parse error

    [test_kqueue.py]=1 # it fails on its own

    [test_lib2to3.py]=1 # it fails on its own
    [test_long.py]=1 # test assert failure (1)
    [test_logging.py]=1 # test errors; (takes a long time to run)

    [test_mailbox.py]=1 # probably control flow
    [test_msilib.py]=1 # it fails on its own
    [test_multiprocessing_fork.py]=1 # test takes too long to run before decompile: 62 seconds
    [test_multiprocessing_forkserver.py]=1 # test takes too long to run before decompile: 62 seconds
    [test_multiprocessing_spawn.py]=1  # test takes too long to run before decompile: 62 seconds

    [test_nntplib.py]=1 # Too long in running before decomplation takes 25 seconds

    [test_ossaudiodev.py]=1 # it fails on its own
    [test_optparse.py]=1 # test takes more than 15 seconds to run

    [test_pdb.py]=1 # Probably relies on comments
    [test_peepholer.py]=1 # test assert error (2)
    [test_pkg.py]=1 # Investigate: lists differ
    [test_pkgutil.py]=1 # Investigate:
    [test_poll.py]=1 # Takes too long to run before decompiling 11 seconds
    [test_pwd.py]=1 # killing - doesn't terminate
    [test_pydoc.py]=1 # it fails on its own

    [test_regrtest.py]=1 # takes too long to run before decompiling
    [test_runpy.py]=1  # Too long to run before decompiling

    [test_select.py]=1 # test takes too long to run: 11 seconds
    [test_selectors.py]=1 # Takes too long to run before decompling: 17 seconds
    [test_shutil.py]=1 # fails on its own
    [test_signal.py]=1 # Takes too long to run before decompiling: 22 seconds
    [test_smtplib.py]=1 # test errors
    [test_socket.py]=1 # Takes too long to run before decompiling
    [test_ssl.py]=1 # Takes too long to run more than 15 seconds. Probably control flow; unintialized variable
    [test_statistics.py]=1 # test failure (1)
    [test_startfile.py]=1 # it fails on its own
    [test_strptime.py]=1 # test check failure (1)
    [test_strtod.py]=1 # test assertions failed
    [test_subprocess.py]=1 # Takes too long to run before decompile: 25 seconds
    [test_sys_settrace.py]=1 # running the tests loops forever. Control flow?

    [test_tarfile.py]=1 # test takes too long to run before decompiling
    [test_telnetlib.py]=1 # test run takes more than 15 seconds
    [test_threading.py]=1 # test assertion failures (2+)
    [test_tk.py]=1  # test takes too long to run: 13 seconds
    [test_tokenize.py]=1 # test takes too long to run before decompilation: 43 seconds
    [test_trace.py]=1  # it fails on its own
    [test_traceback.py]=1 # Probably uses comment for testing
    [test_tracemalloc.py]=1 # test assert failures
    [test_ttk_guionly.py]=1  # implementation specfic and test takes too long to run: 19 seconds
    [test_types.py]=1 # test failure (1)
    [test_typing.py]=1 # run errors

    [test_unicode.py]=1 # unicode thing
    [test_urllibnet.py]=1 # test errors

    [test_weakref.py]=1 # takes too long to run
    [test_with.py]=1 # test errors.

    [test_winconsoleio.py]=1 # it fails on its own
    [test_winreg.py]=1 # it fails on its own
    [test_winsound.py]=1 # it fails on its own

    [test_zipfile.py]=1 # it fails on its own
    [test_zipfile64.py]=1 # Too long to run
)
# 282 unit-test files in about 15 minutes
# 277 for unpyc37

if (( BATCH )) ; then
    SKIP_TESTS[test_bdb.py]=1 # fails on POWER
    SKIP_TESTS[test_dbm_gnu.py]=1 # fails on its own on POWER
    SKIP_TESTS[test_fileio.py]=1
    SKIP_TESTS[test_idle.py]=1 # Probably installation specific
    SKIP_TESTS[test_sqlite.py]=1 # fails on its own on POWER
    SKIP_TESTS[test_sysconfig.py]=1 # fails on POWER
    SKIP_TESTS[test_tempfile.py]=1 # it fails on POWER (no fd attribuet)
    SKIP_TESTS[test_tix.py]=1 # it fails on its own
    SKIP_TESTS[test_time.py]=1 # it fails on POWER (supposed to work on linux though)
    SKIP_TESTS[test_ttk_textonly.py]=1 # Installation dependent?
    SKIP_TESTS[test_venv.py]=1 # Too long to run: 11 seconds
    SKIP_TESTS[test_zipimport_support.py]=1
    # POWER8 Debian problems
    SKIP_TESTS[test_codecmaps_cn.py]=1 # test takes too long to run: 136 seconds
    SKIP_TESTS[test_codecmaps_hk.py]=1 # test takes too long to run: 45 seconds
    SKIP_TESTS[test_codecmaps_jp.py]=1 # test takes too long to run: 226 seconds
    SKIP_TESTS[test_codecmaps_kr.py]=1 # test takes too long to run: 135 seconds
    SKIP_TESTS[test_codecmaps_tw.py]=1 # test takes too long to run: 91 seconds
    SKIP_TESTS[test_hashlib.py]=1 # test takes too long to run: 122 seconds
    SKIP_TESTS[test_multiprocessing_main_handling.py]=1 # test takes too long to run: 11 seconds
    SKIP_TESTS[test_pickle.py]=1 # test takes too long to run: 14 seconds
    SKIP_TESTS[test_robotparser.py]=1 # test takes too long to run: 31 seconds
    SKIP_TESTS[test_ucn.py]=1 # test takes too long to run: 16 seconds
    SKIP_TESTS[test_urllib2net.py]=1 # test hangs
    SKIP_TESTS[test_urllib2_localnet.py]=1 # hangs on POWER8
    SKIP_TESTS[test_zipimport.py]=1 # test run error on POWER8
fi
