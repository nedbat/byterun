SKIP_TESTS=(
    # File "x-python/xpython/vm.py", line 483, in dispatch
    # byteop.inplaceOperator(byte_name[8:])
    # File "x-python/xpython/byteop/byteop.py", line 412, in inplaceOperator
    # x += y
    # TypeError: 'NoneType' object is not callable
    [test_augassign.py]=1

    # File "xpython/byteop/byteop.py", line 288, in call_function_with_args_resolved
    # retval = func(*pos_args, **named_args)
    # RuntimeError: super(): __class__ cell not found
    [test_abc.py]=1

    # File "pyenv/versions/3.6.10/lib/python3.6/aifc.py", line 346, in initfp
    # raise Error('COMM chunk and/or SSND chunk missing')
    # aifc.Error: COMM chunk and/or SSND chunk missing
    [test_aifc.py]=1

    # File "x-python/xpython/byteop/byteop.py", line 288, in call_function_with_args_resolved
    # retval = func(*pos_args, **named_args)
    # RuntimeError: super(): __class__ cell not found
    [test_array.py]=1

    [test_ast.py]=1

    [test_asynchat.py]=1

    [test_asyncore.py]=1

    # PyVMError: Can't find method function attribute; tried '__func__' and '_im_func'
    [test_os.py]=1

    [test___all__.py]=1  # it fails on its own
    [test_argparse.py]=1 # it fails on its own
    [test_asdl_parser.py]=1 # it fails on its own

    # GET_AITER not implemented
    [test_asyncgen.py]=1

    [test_atexit.py]=1  # The atexit test looks for specific comments in error lines

    [test_bdb.py]=1  # probably sys.settrace stuff

    [test_bisect.py]=1  # it fails on its own
    [test_buffer.py]=1  # Takes a long time to run in tests
    [test_builtin.py]=1  # Fails on its own

    [test test_capi.py]=1 # it fails on its own

    # TypeError: __repr__ returned non-string (type NoneType)
    [test_class.py]=1

    # TypeError: can't pickle module objects
    [test_copy.py]=1

    [test_cmd_line.py]=1 # Interactive?
    [test_codecencodings_cn.py]=1 # it fails on its own
    [test_codecencodings_hk.py]=1 # it fails on its own
    [test_codecencodings_iso2022.py]=1 # it fails on its own
    [test_codecencodings_jp.py]=1 # it fails on its own
    [test_codecencodings_kr.py]=1 # it fails on its own
    [test_codecencodings_tw.py]=1 # it fails on its own
    [test_codecmaps_cn.py]=1 # it fails on its own
    [test_codecmaps_hk.py]=1 # it fails on its own
    [test_codecmaps_jp.py]=1 # it fails on its own
    [test_codecmaps_kr.py]=1 # it fails on its own
    [test_codecmaps_tw.py]=1 # it fails on its own
    [test_codecs.py]=1
    [test_collections.py]= # it fails on its own

    # AttributeError: 'traceback' object has no attribute '__traceback__'
    [test_compile.py]=1

    [test_concurrent_futures.py]=1 # Takes long
    [test_contextlib_async.py]=1 # Investigate
    [test_coroutines.py]=1 # parse error
    [test_curses.py]=1 # Parse error
    [test_ctypes.py]=1 # it fails on its own

    [test_datetime.py]=1 # it fails on its own
    [test_dbm_ndbm.py]=1 # it fails on its own
    [test_decimal.py]=1 # Takes to long to run: 20 seconds

    [test_decorators.py]=1

    # TypeError: can't pickle module objects
    [test_defaultdict.py]=1

    [test_devpoll.py]=1 # it fails on its own
    [test_dict.py]=1 # it fails on its own
    [test_dis.py]=1   # We change line numbers - duh!
    [test_doctest.py]=1  # fails on its own
    [test_docxmlrpc.py]=1 # it fails on its own
    [test_dtrace.py]=1 # it fails on its own
    [test_dummy_thread.py]=1 # it fails on its own

    [test_enum.py]=1  #

    # AttributeError: 'traceback' object has no attribute '__traceback__'
    [test_ensurepip.py]=1

    [test_faulthandler.py]=1 # test takes too long to run: 24 seconds
    [test_filecmp.py]=1   # parse error
    [test_file_eintr.py]=1   # parse error

    # AttributeError: 'traceback' object has no attribute '__traceback__'
    [test_fileinput.py]=1

    # AttributeError: 'traceback' object has no attribute '__traceback__'
    [test_finalization.py]=1
    [test_float.py]=1 # it fails on its own
    [test_functools.py]=1 # it fails on its own
    [test_fstring.py]=1 # need to disambiguate leading fstrings from docstrings

    [test_gdb.py]=1 # it fails on its own
    [test_generators.py]=1 # FIXME: Invalid syntax: f2 = lambda : (yield from g())        if False:
    [test_genexps.py]=1 #
    [test_glob.py]=1 #

    # AttributeError: 'traceback' object has no attribute '__traceback__'
    [test_grammar.py]=1

    # AssertionError: f_back.cells: None
    [test_gzip.py]=1

    [test_hashlib.py]=1 # it fails on its own
    [test_heapq.py]=1 # it fails on its own

    [test_io.py]=1 # it fails on its own
    [test_imaplib.py]=1
    [test_inspect.py]=1 # Syntax error Investigate

    # IndexError: index out of range
    [test_itertools.py]=1 # Takes a long time to run

    [test_kqueue.py]=1 # it fails on its own

    [test_lib2to3.py]=1 # it fails on its own


    # KeyError: '/home/rocky/.pyenv/versions/3.6.10/lib/python3.6/linecache.py.missing'
    [test_linecache.py]=1

    [test_logging.py]=1 # it fails on its own
    [test_long.py]=1 #
    [test_lzma.py]=1 # fails on its own

    [test_mailbox.py]=1 # it fails on its own

    # EOFError: EOF read where object expected
    # AttributeError: 'traceback' object has no attribute '__traceback__'
    [test_marshal.py]=1 #

    # TypeError: sequence item 0: expected str instance, int found
    [test_math.py]=1

    [test_msilib.py]=1 # it fails on its own
    [test_multiprocessing_fork.py]=1 # it fails on its own
    [test_multiprocessing_forkserver.py]=1 # it fails on its own
    [test_multiprocessing_main_handling.py]=1 # takes too long -  11 seconds
    [test_multiprocessing_spawn.py]=1 # it fails on its own

    [test_nntplib.py]=1 # test takes too long to run: 31 seconds
    [test_normalization.py]=1 # it fails on its own

    # NameError: name 'ntpath' is not defined
    [test_ntpath.py]=1

    [test_ordered_dict.py]=1 # it fails on its own
    [test_ossaudiodev.py]=1 # it fails on its own

    [test_pdb.py]=1 # Probably introspection
    [test_pickle.py]=1
    [test_pkgimport.py]=1 # it fails on its own
    [test_plistlib.py]=1
    [test_poll.py]=1 # Takes too long 11 seconds
    [test_pprint.py]=1 # it fails on its own
    [test_pyclbr.py]=1 # it fails on its own
    [test_pydoc.py]=1 # it fails on its own

    [test_random.py]=1 # it fails on its own

    # Run doesn't terminate
    [test_range.py]=1

    [test_regrtest.py]=1 # test takes too long to run: 12 seconds

    # AssertionError: 'test_re.py' != 'test_re.pyc'
    # - test_re.py
    # + test_re.pyc
    # ?           +
    [test_re.py]=1

    # File "test_reprlib.py", line 368, in MyContainer
    # @recursive_repr()
    # AttributeError: 'Function' object has no attribute '__qualname__'
    [test_reprlib.py]=1

    [test_runpy.py]=1 # decompile takes too long?

    [test_sax.py]=1 # it fails on its own
    [test_secrets.py]=1 # it fails on its own
    [test_select.py]=1 # test takes too long to run: 11 seconds
    [test_selectors.py]=1 # it fails on its own

    # IndexError: pop from empty list
    [test_sys_setprofile.py]=1

    [test_shutil.py]=1 # it fails on its own
    [test_signal.py]=1 # it fails on its own
    [test_site.py]=1 # it fails on its own
    [test_smtplib.py]=1 # it fails on its own
    [test_socket.py]=1 # long
    [test_socketserver.py]=1
    [test_ssl.py]=1 # it fails on its own
    [test_startfile.py]=1 # it fails on its own
    [test_statistics.py]=1 # it fails on its own

    # AttributeError: 'traceback' object has no attribute '__traceback__'
    [test_string_literals.py]=1

    [test_strtod.py]=1 # it fails on its own
    [test_struct.py]=1  # test assertion errors
    [test_subprocess.py]=1

    # AssertionError: 56 != 48 : wrong size for <class 'xpython.pyobj.Cell'>: got 56, expected 48
    # Unavoidable: we compare internal cell size with our Cell size
    [test_sys.py]=1 #

    # We don't support sys.settrace()
    [test_sys_settrace.py]=1

    [test_tarfile.py]=1 # it fails on its own
    [test_telnetlib.py]=1 # takes more than 15 seconds to run
    [test_thread.py]=1 # it fails on its own
    [test_threading.py]=1

    # byteCode = byteint(co_code[opoffset])
    # IndexError: index out of range
    [test_threaded_import.py]=1

    [test_threadsignals.py]=1

    [test_timeout.py]=1 # takes too long to run: 18 seconds
    [test_tix.py]=1 # it fails on its own
    [test_tk.py]=1 # it fails on its own
    [test_tokenize.py]=1 # test takes too long to run: 80 seconds
    [test_trace.py]= # it fails on its own

    [test_tracemalloc.py]=1
    [test_ttk_guionly.py]= # it fails on its own
    [test_ttk_textonly.py]=1 # it fails on its own
    [test_turtle.py]=1 # it fails on its own

    # exec(ASYNCIO_TESTS)
    # NameError: name 'TypeVar' is not defined
    [test_typing.py]=1 #

    [test_ucn.py]=1 # it fails on its own
    [test_urllib2_localnet.py]=1 # long
    [test_urllib2net.py]=1 # it fails on its own
    [test_urllib2.py]=1 # it fails on its own
    [test_urllibnet.py]=1 # it fails on its own
    [test_urllib.py]=1 # it fails on its own

    [test_venv.py]=1 # test takes too long to run: 13 seconds

    [test_weakref.py]=1
    [test_winconsoleio.py]=1 # it fails on its own
    [test_winreg.py]=1 # it fails on its own
    [test_winsound.py]=1 # it fails on its own

    # Our Cell vs internal cell
    [test_with.py]=1

    [test_xmlrpc.py]=1 # it fails on its own

    [test_zipfile.py]=1 # Too long - 11 seconds
    [test_zipfile64.py]=1
    [test_zipimport_support.py]=1  # fails on its own
)
# 237 unit-test files in about 7 minutes

if (( BATCH )) ; then
    SKIP_TESTS[test_codeccallbacks.py]=1
    SKIP_TESTS[test_complex.py]=1 # Something funky with POWER8

    # locale on test machine is probably customized
    SKIP_TESTS[test__locale.py]=1
fi
