SKIP_TESTS=(
    # if value.__traceback__ is not tb:
    # AttributeError: 'Traceback' object has no attribute '__traceback__'
    [test_codeccallbacks.py]=1

    # File "x-python/xpython/vm.py", line 483, in dispatch
    # byteop.inplaceOperator(byte_name[8:])
    # File "x-python/xpython/byteop/byteop.py", line 412, in inplaceOperator
    # x += y
    # TypeError: 'NoneType' object is not callable
    [test_augassign.py]=1

    # File "pyenv/versions/3.6.10/lib/python3.6/aifc.py", line 346, in initfp
    # raise Error('COMM chunk and/or SSND chunk missing')
    # aifc.Error: COMM chunk and/or SSND chunk missing
    [test_aifc.py]=1

    # File "xpython/byteop/byteop.py", line 288, in call_function_with_args_resolved
    # retval = func(*pos_args, **named_args)
    # RuntimeError: super(): __class__ cell not found
    [test_abc.py]=1

    [test_array.py]=1
    [test_ast.py]=1

    # exec(ASYNCIO_TESTS)
    # NameError: name 'TypeVar' is not defined
    [test_typing.py]=1 #

    # File "test_abc.py", line 16, in test_factory
    # class TestLegacyAPI(unittest.TestCase):
    # TypeError: __build_class__: func must be a function
    [test_abc.py]=1

    [test_asynchat.py]=1

    # GET_AITER not implemented
    [test_asyncgen.py]=1

    [test_asyncore.py]=1
    [test_base64.py]=1
    [test_baseexception.py]=1
    [test_builtin.py]=1
    [test_binascii.py]=1
    [test_bool.py]=1
    [test_bytes.py]=1
    [test_bz2.py]=1
    [test_calendar.py]=1
    [test_capi.py]=1
    [test_cgi.py]=1
    [test_cgitb.py]=1
    [test_class.py]=1
    [test_cmath.py]=1
    [test_codecs.py]=1
    [test_fork1.py]=1

    # FileNotFoundErrorTraceback (most recent call last):
    # FileNotFoundError: [Errno 2] No such file or directory: '/src/.../xpython/byteop/ieee754.txt'
    # (should be /tmp/test3.7
    [test_math.py]=1

    # xpython.vm.PyVMError: Can't find method function attribute; tried '__func__' and '_im_func'
    [test_decimal.py]=1 # Takes more than 32 seconds to run

    [test_bdb.py]=1 # test assert errors

    # _pickle.PicklingError: Can't pickle <class 'xpython.byteop.byteop.TestNT'>: attribute lookup TestNT on xpython.byteop.byteop failed
    [test_collections.py]=1 # test assert errors

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
    [test_ctypes.py]=1 # it fails on its own
    [test_curses.py]=1 # probably byte string not handled properly
    [test_datetime.py]=1   # Takes too long *before* decompiling
    [test_dbm_ndbm.py]=1 # it fails on its own

    [test_descr.py]=1   # test assertion failures
    [test_devpoll.py]=1 # it fails on its own
    [test_dis.py]=1   # Introspects on line numbers; line numbers don't match in disassembly - duh!
    [test_doctest.py]=1   # fails on its own

    # Can't pickle <enum 'Answer'>: attribute lookup Answer on xpython.byteop.byteop25 failed
    [test_enum.py]=1

    [test_faulthandler.py]=1   # test takes too long before decompiling

    [test_frame.py]=1 # Introspects frame object. VM uses Frame, not frame)
    [test_gdb.py]=1 # it fails on its own
    [test_io.py]=1 # test takes too long to run before decompilation: 37 seconds
    [test_kqueue.py]=1 # it fails on its own
    [test_lib2to3.py]=1 # it fails on its own
    [test_logging.py]=1 # takes too long to run)
    [test_msilib.py]=1 # it fails on its own
    [test_multiprocessing_fork.py]=1 # test takes too long to run before decompile: 62 seconds
    [test_multiprocessing_forkserver.py]=1 # test takes too long to run before decompile: 62 seconds
    [test_multiprocessing_spawn.py]=1  # test takes too long to run before decompile: 62 seconds

    [test_nntplib.py]=1 # Too long in running before decomplation takes 25 seconds

    [test_ossaudiodev.py]=1 # it fails on its own

    [test_pdb.py]=1 # Probably relies on comments
    [test_poll.py]=1 # Takes too long to run before decompiling 11 seconds
    [test_pydoc.py]=1 # it fails on its own

    [test_regrtest.py]=1 # takes too long to run before decompiling
    [test_runpy.py]=1  # Too long to run before decompiling

    [test_selectors.py]=1 # Takes too long to run before decompling: 17 seconds
    [test_shutil.py]=1 # fails on its own
    [test_signal.py]=1 # Takes too long to run before decompiling: 22 seconds
    [test_socket.py]=1 # Takes too long to run before decompiling
    [test_ssl.py]=1 # Takes too long to run more than 15 seconds. Probably control flow; unintialized variable
    [test_startfile.py]=1 # it fails on its own
    [test_subprocess.py]=1 # Takes too long to run before decompile: 25 seconds

    [test_tarfile.py]=1 # test takes too long to run before decompiling
    [test_tk.py]=1  # test takes too long to run: 13 seconds
    [test_tokenize.py]=1 # test takes too long to run before decompilation: 43 seconds
    [test_trace.py]=1  # it fails on its own
    [test_traceback.py]=1 # Probably uses comment for testing
    [test_ttk_guionly.py]=1  # implementation specfic and test takes too long to run: 19 seconds

    [test_weakref.py]=1 # takes too long to run

    [test_winconsoleio.py]=1 # it fails on its own
    [test_winreg.py]=1 # it fails on its own
    [test_winsound.py]=1 # it fails on its own

    [test_zipfile.py]=1 # it fails on its own
    [test_zipfile64.py]=1 # Too long to run
)
# 297 unit-test files in about 8 1/2  minutes

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
