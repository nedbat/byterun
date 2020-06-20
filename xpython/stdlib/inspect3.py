# The changed parts from the Python 3.6 "inspect" module
# We've converted this also to run on Python back to 2.7

import functools
import types
from inspect import isclass, ismethod
from xdis import CO_GENERATOR, CO_COROUTINE

from xdis import PYTHON_VERSION, COMPILER_FLAG_BIT

if PYTHON_VERSION >= 3.3:
    from inspect import (
        FullArgSpec,
        Parameter,
        Signature,
        _NonUserDefinedCallables,
        _void,
        signature,
    )

    if PYTHON_VERSION >= 3.4:
        from inspect import (
            _missing_arguments,
            _signature_bound_method,
            _signature_from_builtin,
            _signature_fromstr,
            _signature_get_partial,
            _signature_get_user_defined_method,
            _signature_is_builtin,
            _too_many,
            unwrap,
        )
    pass
else:
    class Parameter(object):
        # For interpreting Python 3.x from Python 2.x
        # To be filled in...
        pass

    # Note: we don't want to import pyobj and Function since that imports us.

def isgeneratorfunction(object):
    """Return true if the object is a user-defined generator function.

    Generator function objects provide the same attributes as functions.
    See help(isfunction) for a list of attributes."""
    return bool(isGenerator(object) and
                 object.gi_code.co_flags & CO_GENERATOR)

def iscoroutinefunction(object):
    """Return true if the object is a coroutine function.

    Coroutine functions are defined with "async def" syntax.
    """
    return bool((isFunction(object) or ismethod(object)) and
                object.__code__.co_flags & CO_COROUTINE)



# Not Python's 3.2 and before inspect.py
class _empty:
    """Marker object for Signature.empty and Parameter.empty."""
    pass

class MyParameter(Parameter):
    '''Represents a parameter in a function signature.

    Has the following public attributes:

    * name : str
        The name of the parameter as a string.
    * default : object
        The default value for the parameter if specified.  If the
        parameter has no default value, this attribute is set to
        `Parameter.empty`.
    * annotation
        The annotation for the parameter if specified.  If the
        parameter has no annotation, this attribute is set to
        `Parameter.empty`.
    * kind : str
        Describes how argument values are bound to the parameter.
        Possible values: `Parameter.POSITIONAL_ONLY`,
        `Parameter.POSITIONAL_OR_KEYWORD`, `Parameter.VAR_POSITIONAL`,
        `Parameter.KEYWORD_ONLY`, `Parameter.VAR_KEYWORD`.
    '''

    def __init__(self, name, kind, default=_empty, annotation=_empty):

        if kind not in (POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD,
                        VAR_POSITIONAL, KEYWORD_ONLY, VAR_KEYWORD):
            raise ValueError("invalid value for 'Parameter.kind' attribute")
        self._kind = kind

        if default is not _empty:
            if kind in (VAR_POSITIONAL, VAR_KEYWORD):
                msg = '{} parameters cannot have default values'.format(kind)
                raise ValueError(msg)
        self._default = default
        self._annotation = annotation

        if name is _empty:
            raise ValueError('name is a required attribute for Parameter')

        if not isinstance(name, str):
            raise TypeError("name must be a str, not a {!r}".format(name))


        if not (name.isidentifier() or name == ".0"):
            raise ValueError('{!r} is not a valid parameter name'.format(name))

        self._name = name



# from _ParameterKind without the enum that doesn't work on older Pythons
POSITIONAL_ONLY = 0
POSITIONAL_OR_KEYWORD = 1
VAR_POSITIONAL = 2
KEYWORD_ONLY = 3
VAR_KEYWORD = 4

def isFunction(obj):
    return (
        hasattr(obj, "__name__")
        and type(obj).__name__ == "Function"
        and hasattr(obj, "__module__")
        and type(obj).__module__ == "xpython.pyobj"
    )

def isGenerator(obj):
    return (
        hasattr(obj, "__name__")
        and type(obj).__name__ == "Generator"
        and hasattr(obj, "gi_frame")
        and hasattr(obj, "gi_code")
        and hasattr(obj, "gi_running")
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


def getcallargs(*func_and_positional, **named):
    """Get the mapping of arguments to values.

    A dict is returned, with keys the function argument names (including the
    names of the * and ** arguments, if any), and values the respective bound
    values from 'positional' and 'named'."""
    func = func_and_positional[0]
    positional = func_and_positional[1:]
    spec = getfullargspec(func)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = spec
    f_name = func.__name__
    arg2value = {}

    if ismethod(func) and func.__self__ is not None:
        # implicit 'self' (or 'cls' for classmethods) argument
        positional = (func.__self__,) + positional
    num_pos = len(positional)
    num_args = len(args)
    num_defaults = len(defaults) if defaults else 0

    n = min(num_pos, num_args)
    for i in range(n):
        arg2value[args[i]] = positional[i]
    if varargs:
        arg2value[varargs] = tuple(positional[n:])
    possible_kwargs = set(args + kwonlyargs)
    if varkw:
        arg2value[varkw] = {}
    for kw, value in named.items():
        if kw not in possible_kwargs:
            if not varkw:
                raise TypeError(
                    "%s() got an unexpected keyword argument %r" % (f_name, kw)
                )
            arg2value[varkw][kw] = value
            continue
        if kw in arg2value:
            raise TypeError("%s() got multiple values for argument %r" % (f_name, kw))
        arg2value[kw] = value
    if num_pos > num_args and not varargs:
        _too_many(f_name, args, kwonlyargs, varargs, num_defaults, num_pos, arg2value)
    if num_pos < num_args:
        req = args[: num_args - num_defaults]
        for arg in req:
            if arg not in arg2value:
                _missing_arguments(f_name, req, True, arg2value)
        for i, arg in enumerate(args[num_args - num_defaults :]):
            if arg not in arg2value:
                arg2value[arg] = defaults[i]
    missing = 0
    for kwarg in kwonlyargs:
        if kwarg not in arg2value:
            if kwonlydefaults and kwarg in kwonlydefaults:
                arg2value[kwarg] = kwonlydefaults[kwarg]
            else:
                missing += 1
    if missing:
        _missing_arguments(f_name, kwonlyargs, False, arg2value)
    return arg2value


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


def getfullargspec(func):
    """Get the names and default values of a callable object's parameters.

    A tuple of seven things is returned:
    (args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations).
    'args' is a list of the parameter names.
    'varargs' and 'varkw' are the names of the * and ** parameters or None.
    'defaults' is an n-tuple of the default values of the last n parameters.
    'kwonlyargs' is a list of keyword-only parameter names.
    'kwonlydefaults' is a dictionary mapping names from kwonlyargs to defaults.
    'annotations' is a dictionary mapping parameter names to annotations.

    Notable differences from inspect.signature():
      - the "self" parameter is always reported, even for bound methods
      - wrapper chains defined by __wrapped__ *not* unwrapped automatically
    """

    try:
        # Re: `skip_bound_arg=False`
        #
        # There is a notable difference in behaviour between getfullargspec
        # and Signature: the former always returns 'self' parameter for bound
        # methods, whereas the Signature always shows the actual calling
        # signature of the passed object.
        #
        # To simulate this behaviour, we "unbind" bound methods, to trick
        # inspect.signature to always return their first parameter ("self",
        # usually)

        # Re: `follow_wrapper_chains=False`
        #
        # getfullargspec() historically ignored __wrapped__ attributes,
        # so we ensure that remains the case in 3.3+

        sig = _signature_from_callable(
            func, follow_wrapper_chains=False, skip_bound_arg=False, sigcls=Signature
        )
    except Exception as ex:
        # Most of the times 'signature' will raise ValueError.
        # But, it can also raise AttributeError, and, maybe something
        # else. So to be fully backwards compatible, we catch all
        # possible exceptions here, and reraise a TypeError.
        raise TypeError("unsupported callable") # from ex

    args = []
    varargs = None
    varkw = None
    kwonlyargs = []
    defaults = ()
    annotations = {}
    defaults = ()
    kwdefaults = {}

    if sig.return_annotation is not sig.empty:
        annotations["return"] = sig.return_annotation

    for param in sig.parameters.values():
        kind = param.kind
        name = param.name

        if kind is POSITIONAL_ONLY:
            args.append(name)
        elif kind is POSITIONAL_OR_KEYWORD:
            args.append(name)
            if param.default is not param.empty:
                defaults += (param.default,)
        elif kind is VAR_POSITIONAL:
            varargs = name
        elif kind is KEYWORD_ONLY:
            kwonlyargs.append(name)
            if param.default is not param.empty:
                kwdefaults[name] = param.default
        elif kind is VAR_KEYWORD:
            varkw = name

        if param.annotation is not param.empty:
            annotations[name] = param.annotation

    if not kwdefaults:
        # compatibility with 'func.__kwdefaults__'
        kwdefaults = None

    if not defaults:
        # compatibility with 'func.__defaults__'
        defaults = None

    return FullArgSpec(
        args, varargs, varkw, defaults, kwonlyargs, kwdefaults, annotations
    )


def _signature_from_function(cls, func):
    """Private helper: constructs Signature for the given python function."""

    is_duck_function = False
    if not isfunction(func):
        if _signature_is_functionlike(func):
            is_duck_function = True
        else:
            # If it's not a pure Python function, and not a duck type
            # of pure function:
            raise TypeError('%r is not a Python function' % func)

    # parameter_class = cls._parameter_cls
    # if parameter_class != InspectParameter:
    #     MyParameter = parameter_class

    # Parameter information.
    func_code = func.__code__
    pos_count = func_code.co_argcount
    arg_names = func_code.co_varnames
    positional = tuple(arg_names[:pos_count])
    if hasattr(func_code, "co_kwonlyargcount"):
        keyword_only_count = func_code.co_kwonlyargcount
    else:
        keyword_only_count = 0
    keyword_only = arg_names[pos_count:(pos_count + keyword_only_count)]
    if hasattr(func_code, "__annotations__"):
        annotations = func.__annotations__
    else:
        annotations = {}
    defaults = func.__defaults__
    if hasattr(func, "__kwdefaults__"):
        kwdefaults = func.__kwdefaults__
    else:
        kwdefaults = {}

    if defaults:
        pos_default_count = len(defaults)
    else:
        pos_default_count = 0

    parameters = []

    # Non-keyword-only parameters w/o defaults.
    non_default_count = pos_count - pos_default_count
    for name in positional[:non_default_count]:
        annotation = annotations.get(name, _empty)
        parameters.append(MyParameter(name, annotation=annotation,
                                    kind=POSITIONAL_OR_KEYWORD))

    # ... w/ defaults.
    for offset, name in enumerate(positional[non_default_count:]):
        annotation = annotations.get(name, _empty)
        parameters.append(MyParameter(name, annotation=annotation,
                                    kind=POSITIONAL_OR_KEYWORD,
                                    default=defaults[offset]))

    # *args
    if func_code.co_flags & COMPILER_FLAG_BIT["VARARGS"]:
        name = arg_names[pos_count + keyword_only_count]
        annotation = annotations.get(name, _empty)
        parameters.append(MyParameter(name, annotation=annotation,
                                      kind=VAR_POSITIONAL))

    # Keyword-only parameters.
    for name in keyword_only:
        default = _empty
        if kwdefaults is not None:
            default = kwdefaults.get(name, _empty)

        annotation = annotations.get(name, _empty)
        parameters.append(MyParameter(name, annotation=annotation,
                                    kind=KEYWORD_ONLY,
                                    default=default))
    # **kwargs
    if func_code.co_flags & COMPILER_FLAG_BIT["VARKEYWORDS"]:
        index = pos_count + keyword_only_count
        if func_code.co_flags & COMPILER_FLAG_BIT["VARARGS"]:
            index += 1

        name = arg_names[index]
        annotation = annotations.get(name, _empty)
        parameters.append(MyParameter(name, annotation=annotation,
                                      kind=VAR_KEYWORD))

    # Is 'func' is a pure Python function - don't validate the
    # parameters list (for correct order and defaults), it should be OK.
    return cls(parameters,
               return_annotation=annotations.get('return', _empty),
               __validate_parameters__=is_duck_function)


def _signature_from_callable(
    obj, follow_wrapper_chains=True, skip_bound_arg=True, sigcls=None
):

    """Private helper function to get signature for arbitrary
    callable objects.
    """

    # We don't want to import pyobj, since that imports us
    if not xCallable(obj):
        raise TypeError("%r is not a callable object" % obj)

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
                    "unexpected object %r in __signature__ " "attribute" % sig
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
                        "no signature found for builtin type %r" % obj
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
                msg = "no signature found for %r" % obj
                raise ValueError(msg) # from ex

    if sig is not None:
        # For classes and objects we skip the first parameter of their
        # __call__, __new__, or __init__ methods
        if skip_bound_arg:
            return _signature_bound_method(sig)
        else:
            return sig

    if isinstance(obj, types.BuiltinFunctionType):
        # Raise a nicer error message for builtins
        msg = "no signature found for builtin function %r" % obj
        raise ValueError(msg)

    raise ValueError("callable %r is not supported by signature" % obj)

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
        msg = "Failed to import %s (%s: %s)" % (mod_name, type(exc).__name__, exc)
        print(msg)
        exit(2)

    if has_attrs:
        parts = attrs.split(".")
        obj = module
        for part in parts:
            obj = getattr(obj, part)

    if module.__name__ in sys.builtin_module_names:
        print("Can't get info for builtin modules.")
        exit(1)

    from inspect import getsourcefile, getsource, findsource

    if args.details:
        print("Target: %s" % target)
        print("Origin: %s" % getsourcefile(module))
        print("Cached: %s" % module.__cached__)
        if obj is module:
            print("Loader: %r" % (module.__loader__))
            if hasattr(module, "__path__"):
                print("Submodule search path: %s" % module.__path__)
        else:
            try:
                __, lineno = findsource(obj)
            except Exception:
                pass
            else:
                print("Line: %d" % lineno)

        print("\n")
    else:
        print(getsource(obj))


if __name__ == "__main__":
    _main()
