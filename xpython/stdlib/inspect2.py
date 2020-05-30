# We use this code only when we are interpreting Python 2 from Python 3.

# The changed parts from the Python 2.7 "inspect" library.
# We've converted this also to run on Python up to 3.7

from collections import namedtuple
from inspect import ismethod

from xdis import iscode, COMPILER_FLAG_BIT

# For the kinds of specific opcode use we need,
# all 2.x opcodes are compatibile with what is in 2.7
import xdis.opcodes.opcode_27 as opc

ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')

def isFunction(obj):
    return (
        hasattr(obj, "__name__")
        and type(obj).__name__ == "Function"
        and hasattr(obj, "__module__")
        and type(obj).__module__ == "xpython.pyobj"
    )


# ------------------------------------------------ argument list extraction
Arguments = namedtuple('Arguments', 'args varargs keywords')

# It turns in spite of all of the other Python opcode changes,
# out the magic number 90 has always been the number for which
# opcodes with arguments start.

def getargs(co, version):
    """Get information about the arguments accepted by a code object.

    Three things are returned: (args, varargs, varkw), where 'args' is
    a list of argument names (possibly containing nested lists), and
    'varargs' and 'varkw' are the names of the * and ** arguments or None."""

    if not iscode(co):
        raise TypeError('{!r} is not a code object'.format(co))

    nargs = co.co_argcount
    names = co.co_varnames
    args = list(names[:nargs])
    step = 0

    # The following acrobatics are for anonymous (tuple) arguments.
    for i in range(nargs):
        if args[i][:1] in ('', '.'):
            stack, remain, count = [], [], []
            while step < len(co.co_code):
                op = ord(co.co_code[step])
                step = step + 1
                if op >= opc.HAVE_ARGUMENT:
                    opname = opc.opname[op]
                    value = ord(co.co_code[step]) + ord(co.co_code[step+1])*256
                    step = step + 2
                    if opname in ('UNPACK_TUPLE', 'UNPACK_SEQUENCE'):
                        remain.append(value)
                        count.append(value)
                    elif opname in ('STORE_FAST', 'STORE_DEREF'):
                        if opname == 'STORE_FAST':
                            stack.append(names[value])
                        else:
                            stack.append(co.co_cellvars[value])

                        # Special case for sublists of length 1: def foo((bar))
                        # doesn't generate the UNPACK_TUPLE bytecode, so if
                        # `remain` is empty here, we have such a sublist.
                        if not remain:
                            stack[0] = [stack[0]]
                            break
                        else:
                            remain[-1] = remain[-1] - 1
                            while remain[-1] == 0:
                                remain.pop()
                                size = count.pop()
                                stack[-size:] = [stack[-size:]]
                                if not remain: break
                                remain[-1] = remain[-1] - 1
                            if not remain: break
            args[i] = stack[0]

    varargs = None
    if co.co_flags & COMPILER_FLAG_BIT["VARARGS"]:
        varargs = co.co_varnames[nargs]
        nargs = nargs + 1
    varkw = None
    if co.co_flags & COMPILER_FLAG_BIT["VARKEYWORDS"]:
        varkw = co.co_varnames[nargs]
    return Arguments(args, varargs, varkw)

def getargspec(func):
    """Get the names and default values of a function's arguments.

    A tuple of four things is returned: (args, varargs, varkw, defaults).
    'args' is a list of the argument names (it may contain nested lists).
    'varargs' and 'varkw' are the names of the * and ** arguments or None.
    'defaults' is an n-tuple of the default values of the last n arguments.
    """

    if ismethod(func):
        func = func.im_func
    if not isFunction(func):
        raise TypeError('{!r} is not a Python function'.format(func))
    args, varargs, varkw = getargs(func.func_code, func.version)
    return ArgSpec(args, varargs, varkw, func.func_defaults)

ArgInfo = namedtuple('ArgInfo', 'args varargs keywords locals')

def getcallargs(func, *positional, **named):
    """Get the mapping of arguments to values.

    A dict is returned, with keys the function argument names (including the
    names of the * and ** arguments, if any), and values the respective bound
    values from 'positional' and 'named'."""
    args, varargs, varkw, defaults = getargspec(func)
    f_name = func.__name__
    arg2value = {}

    # The following closures are basically because of tuple parameter unpacking.
    assigned_tuple_params = []
    def assign(arg, value):
        if isinstance(arg, str):
            arg2value[arg] = value
        else:
            assigned_tuple_params.append(arg)
            value = iter(value)
            for i, subarg in enumerate(arg):
                try:
                    subvalue = next(value)
                except StopIteration:
                    raise ValueError('need more than %d %s to unpack' %
                                     (i, 'values' if i > 1 else 'value'))
                assign(subarg,subvalue)
            try:
                next(value)
            except StopIteration:
                pass
            else:
                raise ValueError('too many values to unpack')
    def is_assigned(arg):
        if isinstance(arg,str):
            return arg in arg2value
        return arg in assigned_tuple_params
    if ismethod(func) and func.im_self is not None:
        # implicit 'self' (or 'cls' for classmethods) argument
        positional = (func.im_self,) + positional
    num_pos = len(positional)
    num_total = num_pos + len(named)
    num_args = len(args)
    num_defaults = len(defaults) if defaults else 0
    for arg, value in zip(args, positional):
        assign(arg, value)
    if varargs:
        if num_pos > num_args:
            assign(varargs, positional[-(num_pos-num_args):])
        else:
            assign(varargs, ())
    elif 0 < num_args < num_pos:
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at most' if defaults else 'exactly', num_args,
            'arguments' if num_args > 1 else 'argument', num_total))
    elif num_args == 0 and num_total:
        if varkw:
            if num_pos:
                # XXX: We should use num_pos, but Python also uses num_total:
                raise TypeError('%s() takes exactly 0 arguments '
                                '(%d given)' % (f_name, num_total))
        else:
            raise TypeError('%s() takes no arguments (%d given)' %
                            (f_name, num_total))
    for arg in args:
        if isinstance(arg, str) and arg in named:
            if is_assigned(arg):
                raise TypeError("%s() got multiple values for keyword "
                                "argument '%s'" % (f_name, arg))
            else:
                assign(arg, named.pop(arg))
    if defaults:    # fill in any missing values with the defaults
        for arg, value in zip(args[-num_defaults:], defaults):
            if not is_assigned(arg):
                assign(arg, value)
    if varkw:
        assign(varkw, named)
    elif named:
        unexpected = next(iter(named))
        try:
            unicode
        except NameError:
            pass
        else:
            if isinstance(unexpected, unicode):
                unexpected = unexpected.encode(sys.getdefaultencoding(), 'replace')
        raise TypeError("%s() got an unexpected keyword argument '%s'" %
                        (f_name, unexpected))
    unassigned = num_args - len([arg for arg in args if is_assigned(arg)])
    if unassigned:
        num_required = num_args - num_defaults
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at least' if defaults else 'exactly', num_required,
            'arguments' if num_required > 1 else 'argument', num_total))
    return arg2value
