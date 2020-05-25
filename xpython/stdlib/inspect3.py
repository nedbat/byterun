# The changed parts from the Python 3.6 inspect library.

import functools
import types
from inspect import isclass

from xdis import PYTHON3

if PYTHON3 >= 3.3:
    from inspect import _NonUserDefinedCallables, Parameter, Signature, signature, _void

if PYTHON3 >= 3.4:
    from inspect import (
        _signature_bound_method,
        _signature_from_builtin,
        _signature_fromstr,
        _signature_get_partial,
        _signature_get_user_defined_method,
        _signature_is_builtin,
        unwrap,
    )

    if PYTHON3 >= 3.5:
        from inspect import _signature_from_function

    # Note: we don't want to import pyobj and Function since that imports us.


def isFunction(obj):
    return (
        hasattr(obj, "__name__")
        and type(obj).__name__ == "Function"
        and hasattr(obj, "__module__")
        and type(obj).__module__ == "xpython.pyobj"
    )


# A replacement for builtint callable().
def xCallable(obj):
    return callable(obj) or isFunction(object)


def isfunction(object):
    """Return true if the object is a user-defined function.

    Function objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this function was defined
        __code__        code object containing compiled function bytecode
        __defaults__    tuple of any default values for arguments
        __globals__     global namespace in which this function was defined
        __annotations__ dict of parameter annotations
        __kwdefaults__  dict of keyword only parameters with defaults"""
    return isinstance(object, types.FunctionType) or isFunction(object)


def _signature_is_functionlike(obj):
    """Private helper to test if `obj` is a duck type of FunctionType.
    A good example of such objects are functions compiled with
    Cython, which have all attributes that a pure Python function
    would have, but have their code statically compiled.
    """

    if not xCallable(obj) or isclass(obj):
        # All function-like objects are obviously callables,
        # and not classes.
        return False

    name = getattr(obj, "__name__", None)
    code = getattr(obj, "__code__", None)
    defaults = getattr(obj, "__defaults__", _void)  # Important to use _void ...
    kwdefaults = getattr(obj, "__kwdefaults__", _void)  # ... and not None here
    annotations = getattr(obj, "__annotations__", None)

    return (
        isinstance(code, types.CodeType)
        and isinstance(name, str)
        and (defaults is None or isinstance(defaults, tuple))
        and (kwdefaults is None or isinstance(kwdefaults, dict))
        and isinstance(annotations, dict)
    )


def _signature_from_callable(
    obj, *, follow_wrapper_chains=True, skip_bound_arg=True, sigcls
):

    """Private helper function to get signature for arbitrary
    callable objects.
    """

    # We don't want to import pyobj, since that imports us
    if not xCallable(obj):
        raise TypeError("{!r} is not a callable object".format(obj))

    if isinstance(obj, types.MethodType):
        # In this case we skip the first parameter of the underlying
        # function (usually `self` or `cls`).
        sig = _signature_from_callable(
            obj.__func__,
            follow_wrapper_chains=follow_wrapper_chains,
            skip_bound_arg=skip_bound_arg,
            sigcls=sigcls,
        )

        if skip_bound_arg:
            return _signature_bound_method(sig)
        else:
            return sig

    # Was this function wrapped by a decorator?
    if follow_wrapper_chains:
        obj = unwrap(obj, stop=(lambda f: hasattr(f, "__signature__")))
        if isinstance(obj, types.MethodType):
            # If the unwrapped object is a *method*, we might want to
            # skip its first parameter (self).
            # See test_signature_wrapped_bound_method for details.
            return _signature_from_callable(
                obj,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls,
            )

    try:
        sig = obj.__signature__
    except AttributeError:
        pass
    else:
        if sig is not None:
            if not isinstance(sig, Signature):
                raise TypeError(
                    "unexpected object {!r} in __signature__ " "attribute".format(sig)
                )
            return sig

    try:
        partialmethod = obj._partialmethod
    except AttributeError:
        pass
    else:
        if isinstance(partialmethod, functools.partialmethod):
            # Unbound partialmethod (see functools.partialmethod)
            # This means, that we need to calculate the signature
            # as if it's a regular partial object, but taking into
            # account that the first positional argument
            # (usually `self`, or `cls`) will not be passed
            # automatically (as for boundmethods)

            wrapped_sig = _signature_from_callable(
                partialmethod.func,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls,
            )

            sig = _signature_get_partial(wrapped_sig, partialmethod, (None,))
            first_wrapped_param = tuple(wrapped_sig.parameters.values())[0]
            if first_wrapped_param.kind is Parameter.VAR_POSITIONAL:
                # First argument of the wrapped callable is `*args`, as in
                # `partialmethod(lambda *args)`.
                return sig
            else:
                sig_params = tuple(sig.parameters.values())
                assert not sig_params or first_wrapped_param is not sig_params[0]
                new_params = (first_wrapped_param,) + sig_params
                return sig.replace(parameters=new_params)

    if isfunction(obj) or _signature_is_functionlike(obj):
        # If it's a pure Python function, or an object that is duck type
        # of a Python function (Cython functions, for instance), then:
        return _signature_from_function(sigcls, obj)

    if _signature_is_builtin(obj):
        return _signature_from_builtin(sigcls, obj, skip_bound_arg=skip_bound_arg)

    if isinstance(obj, functools.partial):
        wrapped_sig = _signature_from_callable(
            obj.func,
            follow_wrapper_chains=follow_wrapper_chains,
            skip_bound_arg=skip_bound_arg,
            sigcls=sigcls,
        )
        return _signature_get_partial(wrapped_sig, obj)

    sig = None
    if isinstance(obj, type):
        # obj is a class or a metaclass

        # First, let's see if it has an overloaded __call__ defined
        # in its metaclass
        call = _signature_get_user_defined_method(type(obj), "__call__")
        if call is not None:
            sig = _signature_from_callable(
                call,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls,
            )
        else:
            # Now we check if the 'obj' class has a '__new__' method
            new = _signature_get_user_defined_method(obj, "__new__")
            if new is not None:
                sig = _signature_from_callable(
                    new,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls,
                )
            else:
                # Finally, we should have at least __init__ implemented
                init = _signature_get_user_defined_method(obj, "__init__")
                if init is not None:
                    sig = _signature_from_callable(
                        init,
                        follow_wrapper_chains=follow_wrapper_chains,
                        skip_bound_arg=skip_bound_arg,
                        sigcls=sigcls,
                    )

        if sig is None:
            # At this point we know, that `obj` is a class, with no user-
            # defined '__init__', '__new__', or class-level '__call__'

            for base in obj.__mro__[:-1]:
                # Since '__text_signature__' is implemented as a
                # descriptor that extracts text signature from the
                # class docstring, if 'obj' is derived from a builtin
                # class, its own '__text_signature__' may be 'None'.
                # Therefore, we go through the MRO (except the last
                # class in there, which is 'object') to find the first
                # class with non-empty text signature.
                try:
                    text_sig = base.__text_signature__
                except AttributeError:
                    pass
                else:
                    if text_sig:
                        # If 'obj' class has a __text_signature__ attribute:
                        # return a signature based on it
                        return _signature_fromstr(sigcls, obj, text_sig)

            # No '__text_signature__' was found for the 'obj' class.
            # Last option is to check if its '__init__' is
            # object.__init__ or type.__init__.
            if type not in obj.__mro__:
                # We have a class (not metaclass), but no user-defined
                # __init__ or __new__ for it
                if obj.__init__ is object.__init__ and obj.__new__ is object.__new__:
                    # Return a signature of 'object' builtin.
                    return signature(object)
                else:
                    raise ValueError(
                        "no signature found for builtin type {!r}".format(obj)
                    )

    elif not isinstance(obj, _NonUserDefinedCallables):
        # An object with __call__
        # We also check that the 'obj' is not an instance of
        # _WrapperDescriptor or _MethodWrapper to avoid
        # infinite recursion (and even potential segfault)
        call = _signature_get_user_defined_method(type(obj), "__call__")
        if call is not None:
            try:
                sig = _signature_from_callable(
                    call,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls,
                )
            except ValueError as ex:
                msg = "no signature found for {!r}".format(obj)
                raise ValueError(msg) from ex

    if sig is not None:
        # For classes and objects we skip the first parameter of their
        # __call__, __new__, or __init__ methods
        if skip_bound_arg:
            return _signature_bound_method(sig)
        else:
            return sig

    if isinstance(obj, types.BuiltinFunctionType):
        # Raise a nicer error message for builtins
        msg = "no signature found for builtin function {!r}".format(obj)
        raise ValueError(msg)

    raise ValueError("callable {!r} is not supported by signature".format(obj))


def _main():
    """ Logic for inspecting an object given at command line """
    import argparse
    import importlib

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "object",
        help="The object to be analysed. " "It supports the 'module:qualname' syntax",
    )
    parser.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Display info about the module rather than its source code",
    )

    args = parser.parse_args()

    target = args.object
    mod_name, has_attrs, attrs = target.partition(":")
    import sys

    try:
        obj = module = importlib.import_module(mod_name)
    except Exception as exc:
        msg = "Failed to import {} ({}: {})".format(mod_name, type(exc).__name__, exc)
        print(msg, file=sys.stderr)
        exit(2)

    if has_attrs:
        parts = attrs.split(".")
        obj = module
        for part in parts:
            obj = getattr(obj, part)

    if module.__name__ in sys.builtin_module_names:
        print("Can't get info for builtin modules.", file=sys.stderr)
        exit(1)

    from inspect import getsourcefile, getsource, findsource

    if args.details:
        print("Target: {}".format(target))
        print("Origin: {}".format(getsourcefile(module)))
        print("Cached: {}".format(module.__cached__))
        if obj is module:
            print("Loader: {}".format(repr(module.__loader__)))
            if hasattr(module, "__path__"):
                print("Submodule search path: {}".format(module.__path__))
        else:
            try:
                __, lineno = findsource(obj)
            except Exception:
                pass
            else:
                print("Line: {}".format(lineno))

        print("\n")
    else:
        print(getsource(obj))


if __name__ == "__main__":
    _main()
