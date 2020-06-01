# FIXME: There is probably way to use importer to simplify this.  The
# problem is that historically this has been a big mess, which changes
# a lot and we are interested in supporting (some) historical versions
# of Python.

def get_byteop(vm, python_version, is_pypy):
    """Get Python byteop for given integer Python version, e.g. 2.7, 3.2, 3.5..., and the
    platform is_pypy. vm.VMError will be raised if we can't find a suitable version.
    """

    int_vers = int(python_version * 10)

    if int_vers < 30:
        if int_vers >= 26:
            if int_vers == 27:
                if is_pypy:
                    from xpython.byteop.byteop27pypy import ByteOp27PyPy

                    byteop = ByteOp27PyPy(vm)
                else:
                    from xpython.byteop.byteop27 import ByteOp27

                    byteop = ByteOp27(vm)
            else:
                assert int_vers == 26
                from xpython.byteop.byteop26 import ByteOp26

                byteop = ByteOp26(vm)
                pass
        else:
            if int_vers == 25:
                from xpython.byteop.byteop25 import ByteOp25

                byteop = ByteOp25(vm)
            elif int_vers == 24:
                from xpython.byteop.byteop24 import ByteOp24

                byteop = ByteOp24(vm)
                pass
            pass
    else:
        # 3.0 or greater
        if int_vers < 35:
            if int_vers == 32:
                if is_pypy:
                    from xpython.byteop.byteop32pypy import ByteOp32PyPy

                    byteop = ByteOp32PyPy(vm)
                else:
                    from xpython.byteop.byteop32 import ByteOp32

                    byteop = ByteOp32(vm)
            elif int_vers == 33:
                from xpython.byteop.byteop33 import ByteOp33

                byteop = ByteOp33(vm)
            elif int_vers == 34:
                from xpython.byteop.byteop34 import ByteOp34

                byteop = ByteOp34(vm)
            else:
                raise vm.VMEerror("Version %s not supported" % python_version)
        else:
            if int_vers == 35:
                if is_pypy:
                    from xpython.byteop.byteop35pypy import ByteOp35PyPy

                    byteop = ByteOp35PyPy(vm)
                else:
                    from xpython.byteop.byteop35 import ByteOp35

                    byteop = ByteOp35(vm)
            elif int_vers == 36:
                if is_pypy:
                    from xpython.byteop.byteop36pypy import ByteOp36PyPy

                    byteop = ByteOp36PyPy(vm)
                else:
                    from xpython.byteop.byteop36 import ByteOp36

                    byteop = ByteOp36(vm)
            elif int_vers == 37:
                from xpython.byteop.byteop37 import ByteOp37

                byteop = ByteOp37(vm)
            else:
                raise vm.VMEerror("Version %s not supported" % python_version)
            pass
        pass
    return byteop
