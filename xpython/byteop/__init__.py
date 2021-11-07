# FIXME: There is probably way to use importer to simplify this.  The
# problem is that historically this has been a big mess, which changes
# a lot and we are interested in supporting (some) historical versions
# of Python.


def get_byteop(vm, python_version, is_pypy):
    """Get Python byteop for given integer Python version, e.g. 2.7, 3.2, 3.5..., and the
    platform is_pypy. vm.VMError will be raised if we can't find a suitable version.
    """

    python_version = python_version[:2]
    if python_version < (3, 0):
        if python_version >= (2, 6):
            if python_version == (2, 7):
                if is_pypy:
                    from xpython.byteop.byteop27pypy import ByteOp27PyPy

                    byteop = ByteOp27PyPy(vm)
                else:
                    from xpython.byteop.byteop27 import ByteOp27

                    byteop = ByteOp27(vm)
            else:
                assert python_version == (2, 6)
                from xpython.byteop.byteop26 import ByteOp26

                byteop = ByteOp26(vm)
                pass
        else:
            if python_version == (2, 5):
                from xpython.byteop.byteop25 import ByteOp25

                byteop = ByteOp25(vm)
            elif python_version == (2, 4):
                from xpython.byteop.byteop24 import ByteOp24

                byteop = ByteOp24(vm)
                pass
            pass
    else:
        # 3.0 or greater
        if python_version < (3, 5):
            if python_version == (3, 2):
                if is_pypy:
                    from xpython.byteop.byteop32pypy import ByteOp32PyPy

                    byteop = ByteOp32PyPy(vm)
                else:
                    from xpython.byteop.byteop32 import ByteOp32

                    byteop = ByteOp32(vm)
            elif python_version == (3, 3):
                from xpython.byteop.byteop33 import ByteOp33

                byteop = ByteOp33(vm)
            elif python_version == (3, 4):
                from xpython.byteop.byteop34 import ByteOp34

                byteop = ByteOp34(vm)
            else:
                raise vm.VMEerror("Version %s not supported" % python_version)
        else:
            if python_version == (3, 5):
                if is_pypy:
                    from xpython.byteop.byteop35pypy import ByteOp35PyPy

                    byteop = ByteOp35PyPy(vm)
                else:
                    from xpython.byteop.byteop35 import ByteOp35

                    byteop = ByteOp35(vm)
            elif python_version == (3, 6):
                if is_pypy:
                    from xpython.byteop.byteop36pypy import ByteOp36PyPy

                    byteop = ByteOp36PyPy(vm)
                else:
                    from xpython.byteop.byteop36 import ByteOp36

                    byteop = ByteOp36(vm)
            elif python_version == (3, 7):
                if is_pypy:
                    from xpython.byteop.byteop37pypy import ByteOp37PyPy

                    byteop = ByteOp37PyPy(vm)
                else:
                    from xpython.byteop.byteop37 import ByteOp37

                    byteop = ByteOp37(vm)

            elif python_version == (3, 8):
                if is_pypy:
                    from xpython.byteop.byteop38pypy import ByteOp38PyPy

                    byteop = ByteOp38PyPy(vm)
                else:
                    from xpython.byteop.byteop38 import ByteOp38

                    byteop = ByteOp38(vm)

            elif python_version == (3, 9):
                from xpython.byteop.byteop39 import ByteOp39

                byteop = ByteOp39(vm)
            else:
                raise vm.VMEerror("Version %s not supported" % python_version)
            pass
        pass
    return byteop
