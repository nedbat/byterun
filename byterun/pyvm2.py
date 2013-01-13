# pyvm2 by Paul Swartz (z3p), from http://www.twistedmatrix.com/users/z3p/
"""
Security issues in running an open python interpreter:

1. importing modules (sys, os, perhaps anything implemented in C?)
2. large objects (range(999999))
3. heavy math (999999**99999)
4. infinite loops (while 1: pass)

I think the policy should be "disallow by default" and if users complain,
the feature can be added.

Solutions to above problems:
1.  only allow access to certian parts of modules / disallow the module entirely
    see SysModule() below, maybe turn it into a generic module wrapper?
2.  this was solved by checking for range in allowCFunction
    are there other C methods that may return large objects?
3.  the only way I can see to fix this is a check in BINARY_POW/INPLACE_POW
    perhaps also check BINARY_MUL/INPLACE_MUL?  I think the ADD/SUB/MOD/XOR
    functions are OK.
4.  this was solved with the absolute byte code counter.

Maybe I should follow the RExec interface?  I think the security issues were
in how it was implemented, not in the API.
On second thought, their API is very strange.

Ideas for a Python VM written in Python:
1.  running the byte codes as a specific user (useful for running multiple
    python interpreters for multiple users in one process)
2.  faked threading.  run a set number of byte codes, then switch to a second 'Thread' and run the byte codes, repeat.
"""

import operator, dis, new, inspect, copy, sys
CO_GENERATOR = 32 # flag for "this code uses yield"

class Cell:
    dontAccess = ['deref', 'set', 'get']
    def __init__(self):
        self.deref = None

    def set(self, deref):
        self.deref = deref

    def get(self):
        return self.deref

class Frame:
    readOnly = ['f_back', 'f_code', 'f_locals', 'f_globals', 'f_builtins',
                'f_restricted', 'f_lineno', 'f_lasti']
    dontAccess = ['_vm', '_cells', '_blockStack', '_generator']

    def __init__(self, f_code, f_globals, f_locals, vm):
        self._vm = vm
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals
        self.f_back = vm.frame()
        if self.f_back:
            self.f_builtins = self.f_back.f_builtins
        else:
            self.f_builtins = f_locals['__builtins__']
            if hasattr(self.f_builtins, '__dict__'):
                self.f_builtins = self.f_builtins.__dict__
        self.f_restricted = 1
        self.f_lineno = f_code.co_firstlineno
        self.f_lasti = 0
        if f_code.co_cellvars:
            self._cells = {}
            if not self.f_back._cells:
                self.f_back._cells = {}
            for var in f_code.co_cellvars:
                self.f_back._cells[var] = self._cells[var] = Cell()
                if self.f_locals.has_key(var):
                    self._cells[var].set(self.f_locals[var])
        else:
            self._cells = None
        if f_code.co_freevars:
            if not self._cells:
                self._cells = {}
            for var in f_code.co_freevars:
                self._cells[var] = self.f_back._cells[var]
        self._blockStack = []

    def __str__(self):
        return '<frame object at 0x%s>' % hex(id(self))[2:].upper().zfill(8)

class Function:
    readOnly = ['func_name', 'func_globals', 'func_closure']
    dontAccess = ['_vm']

    def __init__(self, func_code, func_doc, func_defaults, func_closure, vm):
        self._vm = vm
        self.func_code = func_code
        self.func_name = func_code.co_name
        self.func_doc = func_doc
        self.func_defaults = func_defaults
        self.func_globals = vm.frame().f_globals
        self.func_dict = vm.frame().f_locals
        self.func_closure = func_closure

    def __str__(self):
        return '<function %s at 0x%s>' % (self.func_name,
                                          hex(id(self))[2:].upper().zfill(8))

    __repr__ = __str__

    def __call__(self, *args, **kw):
        if len(args) < self.func_code.co_argcount:
            if not self.func_defaults:
                if self.func_code.co_argcount == 0:
                    argCount = 'no arguments'
                elif self.func_code.co_argcount == 1:
                    argCount = 'exactly 1 argument'
                else:
                    argCount = 'exactly %i arguments' % self.func_code.co_argcount
                raise TypeError, '%s() takes %s (%s given)' % (self.func_name,
                                                               argCount, len(args))
            else:
                defArgCount = len(self.func_defaults)
                args.extend(self.func_defaults[-(self.func_code.co_argcount - len(args)):])
        self._vm.loadCode(self.func_code, args, kw, self.func_globals, self.func_dict)

class Generator:
    readOnly = ['gi_frame', 'gi_running']
    dontAccess = ['_vm', '_savedstack']

    def __init__(self, g_frame, vm):
        self.gi_frame = g_frame
        self.gi_running = 0
        self._vm = copy.copy(vm)
        self._vm._stack = []
        self._vm._returnValue = None
        self._vm._lastException = (None, None, None)
        self._vm._frames = copy.copy(vm._frames)
        self._vm._frames.append(g_frame)

    def __iter__(self):
        return self

    def next(self):
        self.gi_running = 1
        return self._vm.run()

class Class:
    dontAccess = ['_name', '_bases', '_locals']
    def __init__(self, name, bases, methods):
        self._name = name
        self._bases = bases
        self._locals = methods
    def __call__(self, *args, **kw):
        return Object(self, self._name, self._bases, self._locals, args, kw)
    def __str__(self):
        return '<class %s at %s>' % (self._name, 
                                     hex(id(self))[2:].upper().zfill(8))
    __repr__ = __str__
    def isparent(self, obj):
        if not isinstance(obj, Object):
            return 0
        if obj._class is self:
            return 1
        if self in obj._bases:
            return 1
        return 0

class Object:
    def __init__(self, _class, name, bases, methods, args, kw):
        self._class = _class
        self._name = name
        self._bases = bases
        self._locals = methods
        if methods.has_key('__init__'):
            methods['__init__'](self, *args, **kw)
    def __str__(self):
        return '<%s instance at %s>' % (self._name,
                                        hex(id(self))[2:].upper().zfill(8))
    __repr__ = __str__
        
class Method:
    readOnly = ['im_self', 'im_class', 'im_func']
    def __init__(self, object, _class, func):
        self.im_self = object
        self.im_class = _class
        self.im_func = func
    def __str__(self):
        if self.im_self:
            return '<bound method %s.%s of %s>' % (self.im_self._name,
                                                   self.im_func.func_name,
                                                   str(self.im_self))
        else:
            return '<unbound method %s.%s>' % (self.im_class._name,
                                               self.im_func.func_name)
    __repr__ = __str__

UNARY_OPERATORS = {
    'POSITIVE': operator.pos,
    'NEGATIVE': operator.neg,
    'NOT':      operator.not_,
    'CONVERT':  (lambda x: `x`),
    'INVERT':   operator.invert,
}

BINARY_OPERATORS = {
    'POWER':    pow,
    'MULTIPLY': operator.mul,
    'DIVIDE':   operator.div,
    'MODULO':   operator.mod,
    'ADD':      operator.add,
    'SUBTRACT': operator.sub,
    'SUBSCR':   operator.getitem,
    'LSHIFT':   operator.lshift,
    'RSHIFT':   operator.rshift,
    'AND':      operator.and_,
    'XOR':      operator.xor,
    'OR':       operator.or_,
}

INPLACE_OPERATORS = { # these are execed
    'POWER':    'x**=y',
    'MULTIPLY': 'x*=y',
    'DIVIDE':   'x/=y',
    'MODULO':   'x%=y',
    'ADD':      'x+=y',
    'SUBTRACT': 'x-=y',
    'LSHIFT':   'x>>=y',
    'RSHIFT':   'x<<=y',
    'AND':      'x&=y',
    'XOR':      'x^=y',
    'OR':       'x|=y',
}
    
COMPARE_OPERATORS = [
    operator.lt,
    operator.le,
    operator.eq,
    operator.ne,
    operator.gt,
    operator.ge,
    operator.contains,
    lambda x,y: x not in y,
    lambda x,y: x is y,
    lambda x,y: x is not y,
    lambda x,y: issubclass(x, Exception) and (x is y)
]
    
class VirtualMachine:
    def __init__(self):
        self._frames = [] # list of current stack frames
        self._stack = [] # current stack
        self._returnValue = None
        self._lastException = (None, None, None)

    def frame(self):
        return self._frames and self._frames[-1] or None

    def pop(self):
        return self._stack.pop()
    def push(self, thing):
        self._stack.append(thing)

    def loadCode(self, code, args = [], kw = {}, f_globals = None, f_locals = None):
        if f_globals:
            f_globals = f_globals
            if not f_locals:
                f_locals = f_globals
        elif self.frame():
            f_globals = self.frame().f_globals
            f_locals = {}
        else:
            f_globals = f_locals = globals()
        for i in range(code.co_argcount):
            name = code.co_varnames[i]
            if i < len(args):
                if kw.has_key(name):
                    raise TypeError, "got multiple values for keyword argument '%s'" % name
                else:
                    f_locals[name] = args[i]
            else:
                if kw.has_key(name):
                    locals[name] = kw[name]
                else:
                    raise TypeError, "did not get value for argument '%s'" % name
        frame = Frame(code, f_globals, f_locals, self)
        self._frames.append(frame)

    def run(self):
        while self._frames:
            # pre will go here
            frame = self.frame()
            byte = frame.f_code.co_code[frame.f_lasti]
            frame.f_lasti += 1
            byteCode = ord(byte)
            byteName = dis.opname[byteCode]
            arg = None
            if byteCode >= dis.HAVE_ARGUMENT:
                arg = frame.f_code.co_code[frame.f_lasti:frame.f_lasti+2]
                frame.f_lasti += 2
                intArg = ord(arg[0]) + (ord(arg[1])<<8)
                if byteName == 'CALL_FUNCTION':
                    arg = map(ord, arg)
                elif byteCode in dis.hasconst:
                    arg = frame.f_code.co_consts[intArg]
                elif byteCode in dis.hasfree:
                    if intArg < len(frame.f_code.co_cellvars):
                        arg = frame.f_code.co_cellvars[intArg]
                    else:
                        arg = frame.f_code.co_freevars[intArg-len(frame.f_code.co_cellvars)]
                elif byteCode in dis.hasname:
                    arg = frame.f_code.co_names[intArg]
                elif byteCode in dis.hasjrel:
                    arg = frame.f_lasti + intArg
                elif byteCode in dis.hasjabs:
                    arg = intArg
                elif byteCode in dis.haslocal:
                    arg = frame.f_code.co_varnames[intArg]
                else:
                    arg = intArg
            #print len(self._frames), byteName, arg
            finished = 0
            try:
                if byteName.startswith('UNARY_'):
                    self.unaryOperation(byteName)
                elif byteName.startswith('BINARY_'):
                    self.binaryOperator(byteName)
                elif byteName.startswith('INPLACE_'):
                    self.inplaceOperator(byteName)
                elif byteName.find('SLICE') != -1:
                    self.sliceOperator(byteName)
                else:
                    # dispatch
                    func = getattr(self, 'byte_%s' % byteName, None)
                    if not func:
                        raise ValueError, "unknown bytecode type: %s" % byteName
                    if byteCode >= dis.HAVE_ARGUMENT:
                        arguments = [arg]
                    else:
                        arguments = []
                    finished =  func(*arguments)
                #print len(self._frames), self._stack
                if finished:
                    self._frames.pop()
                    self.push(self._returnValue)
                if self._lastException[0]:
                    self._lastException = (None, None, None)
            except:
                while self._frames and not self.frame()._blockStack:
                    self._frames.pop()
                if not self._frames:
                    raise
                self._lastException = sys.exc_info()[:2] + (None,)
                while 1:
                    if not self._frames:
                        raise
                    block = self.frame()._blockStack.pop()
                    if block[0] in ('except', 'finally'):
                        if block[0] == 'except':
                            self.push(self._lastException[2])
                            self.push(self._lastException[1])
                            self.push(self._lastException[0])
                        self.frame().f_lasti = block[1]
                        break
                    while not self.frame()._blockStack:
                        self._frames.pop()
                        if not self._frames():
                            break
                
        if self._lastException[0]:
            e1, e2, e3 = self._lastException
            raise e1, e2, e3
        return self._returnValue

    def unaryOperator(self, op):
        op = op[6:]
        one = self.pop()
        self.push(UNARY_OPERATORS[op](one))

    def binaryOperator(self, op):
        op = op[7:]
        one = self.pop()
        two = self.pop()
        self.push(BINARY_OPERATORS[op](two, one))

    def inplaceOperator(self, op):
        op = op[9:]
        one = self.pop()
        two = self.pop()
        exec INPLACE_OPERATORS[op] in {'x':two, 'y':one}

    def sliceOperator(self, op):
        start = 0
        end = None # we will take this to mean end
        op, count = op[:-2], int(op[-1])
        if count == 1:
            start = self.pop()
        elif count == 2:
            end = self.pop()
        elif count == 3:
            end = self.pop()
            start = self.pop()
        l = self.pop()
        if end == None:
            end = len(l)
        if op.startswith('STORE_'):
            l[start:end] = self.pop()
            self.push(l)
        elif op.startswith('DELETE_'):
            del l[start:end]
            self.push(l)
        else:
            self.push(l[start:end])

    def byte_DUP_TOP(self):
        item = self.pop()
        self.push(item)
        self.push(item)

    def byte_POP_TOP(self):
        self.pop()

    def byte_STORE_SUBSCR(self):
        ind = self.pop()
        l = self.pop()
        item = self.pop()
        l[ind] = item
        self.push(item)
        self.push(l)
        self.push(ind)

    def byte_DELETE_SUBSCR(self):
        ind = self.pop()
        l = self.pop()
        del l[ind]
        self.push(l)
        self.push(ind)

    def byte_PRINT_EXPR(self):
        print self.pop()

    def byte_PRINT_ITEM(self):
        print self.pop(),

    def byte_PRINT_ITEM_TO(self):
        item = self.pop()
        to = self.pop()
        print >>to, item,
        self.push(to)

    def byte_PRINT_NEWLINE(self):
        print

    def byte_PRINT_ITEM_TO(self):
        to = self.pop()
        print >>to , ''
        self.push(to)

    def byte_BREAK_LOOP(self):
        block = self.frame()._blockStack.pop()
        while block[0] != 'loop':
            block = self.frame()._blockStack.pop()
        self.frame().f_lasti = block[1]

    def byte_LOAD_LOCALS(self):
        self.push(self.frame().f_locals)

    def byte_RETURN_VALUE(self):
        self._returnValue = self.pop()
        func = self.pop()
        self.push(func)
        if isinstance(func, Object):
            self._frames.pop()
        else:
            return 1

    def byte_YIELD_VALUE(self):
        value = self.pop() # since we're running in a different VM
        self._returnValue = value
        return 1

    def byte_IMPORT_STAR(self):
        mod = self.pop()
        for attr in mod:
            if attr[0] != '_':
                self.frame().f_locals[attr] = getattr(mod, attr)

    def byte_EXEC_STMT(self):
        one = self.pop()
        two = self.pop()
        three = self.pop()
        exec three in two, one

    def byte_POP_BLOCK(self):
        self.frame()._blockStack.pop()

    def byte_END_FINALLY(self):
        if self._lastException[0]:
            raise self._lastException[0], self._lastException[1], self._lastException[2]
        else:
            return 1

    def byte_BUILD_CLASS(self):
        methods = self.pop()
        bases = self.pop()
        name = self.pop()
        self.push(Class(name, bases, methods))

    def byte_STORE_NAME(self, name):
        self.frame().f_locals[name] = self.pop()

    def byte_DELETE_NAME(self, name):
        del self.frame().f_locals[name]

    def byte_UNPACK_SEQUENCE(self, count):
        l = self.pop()
        for i in range(len(l)-1, 0, -1):
            self.push(l[i])

    def byte_DUP_TOPX(self, count):
        items = [self.pop() for i in range(count)]
        items.reverse()
        [self.push(i) for i in items]

    def byte_STORE_ATTR(self, name):
        obj = self.pop()
        setattr(obj, name, self.pop())

    def byte_DELETE_ATTR(self, name):
        obj = self.pop()
        delattr(obj, name)

    def byte_LOAD_CONST(self, const):
        self.push(const)

    def byte_LOAD_NAME(self, name):
        frame = self.frame()
        if frame.f_locals.has_key(name):
            item = frame.f_locals[name]
        elif frame.f_globals.has_key(name):
            item = frame.f_globals[name]
        elif frame.f_builtins.has_key(name):
            item = frame.f_builtins[name]
        else:
            self.lastException = (NameError, NameError("name '%s' not found" % name),
                                  None) # can't do tb object yet
                                  
            self.raiseException()
            return
        self.push(item)

    def byte_BUILD_TUPLE(self, count):
        self.push(tuple([self.pop() for i in xrange(count)]))

    def byte_BUILD_LIST(self, count):
        self.push([self.pop() for i in xrange(count)])

    def byte_BUILD_MAP(self, zero):
        assert zero == 0
        self.push({})

    def byte_LOAD_ATTR(self, attr):
        obj = self.pop()
        if isinstance(obj, (Object, Class)):
            val = obj._locals[attr]
        else:
            val = getattr(obj, attr)
        if isinstance(obj, Object) and isinstance(val, Function):
            val = Method(obj, obj._class, val)
        elif isinstance(obj, Class) and isinstance(val, Function):
            val = Method(None, obj, val)
        self.push(val)

    def byte_COMPARE_OP(self, opnum):
        one = self.pop()
        two = self.pop()
        self.push(COMPARE_OPERATORS[opnum](two, one))

    def byte_IMPORT_NAME(self, name):
        self.push(__import__(name))

    def byte_IMPORT_FROM(self, name):
        mod = self.pop()
        self.push(mod)
        self.push(getattr(mod, name))

    def byte_JUMP_IF_TRUE(self, jump):
        val = self.pop()
        self.push(val)
        if val:
            self.frame().f_lasti = jump

    def byte_JUMP_IF_FALSE(self, jump):
        val = self.pop()
        self.push(val)
        if not val:
            self.frame().f_lasti = jump

    def byte_JUMP_FORWARD(self, jump):
        self.frame().f_lasti = jump

    def byte_JUMP_ABSOLUTE(self, jump):
        self.frame().f_lasti = jump

    def byte_LOAD_GLOBAL(self, name):
        f = self.frame()
        if f.f_globals.has_key(name):
            self.push(f.f_globals[name])
        elif f.f_builtins.has_key(name):
            self.push(f.f_builtins[name])
        else:
            self.lastException = (NameError, NameError("name '%s' is not defined" % name),
                                  None)
            self.raiseException()
        

    def byte_SETUP_LOOP(self, dest):
        self.frame()._blockStack.append(('loop', dest))

    def byte_SETUP_EXCEPT(self, dest):
        self.frame()._blockStack.append(('except', dest))

    def byte_SETUP_FINALLY(self, dest):
        self.frame()._blockStack.append(('finally', dest))

    def byte_LOAD_FAST(self, name):
        self.push(self.frame().f_locals[name])

    def byte_STORE_FAST(self, name):
        self.frame().f_locals[name] = self.pop()

    def byte_LOAD_CLOSURE(self, name):
        self.push(self.frame()._cells[name])

    def byte_LOAD_DEREF(self, name):
        self.push(self.frame()._cells[name].get())

    def byte_SET_LINENO(self, lineno):
        self.frame().f_lineno = lineno

    def byte_CALL_FUNCTION(self, (lenPos, lenKw)):
        kw = {}
        for i in xrange(lenKw):
            value = self.pop()
            key = self.pop()
            kw[key] = value
        args = []
        for i in xrange(lenPos):
            args.insert(0, self.pop())
        func = self.pop()
        frame = self.frame()
        if hasattr(func, 'im_func'): # method
            if func.im_self:
                args.insert(0, func.im_self)
            if not func.im_class.isparent(args[0]):
                raise TypeError, 'unbound method %s() must be called with %s instance as first argument (got %s instead)' % (func.im_func.func_name, func.im_class._name, type(args[0]))
            func = func.im_func
        if hasattr(func, 'func_code'):
            self.loadCode(func.func_code, args, kw)
            if func.func_code.co_flags & CO_GENERATOR:
                raise NotImplementedError, "cannot do generators ATM"
                gen = Generator(self.frame(), self)
                self._frames.pop()._generator = gen
                self.push(gen)
        else:
            self.push(func(*args, **kw))

    def byte_MAKE_FUNCTION(self, argc):
        defaults = []
        for i in xrange(argc):
            defaults.insert(0, self.pop())
        code = self.pop()
        self.push(Function(code, None, defaults, None, self))

    def byte_MAKE_CLOSURE(self, argc):
        code = self.pop()
        defaults = []
        for i in xrange(argc):
            defaults.insert(0, self.pop())
        closure = []
        if code.co_freevars:
            for i in code.co_freevars:
                closure.insert(0, self.pop())
        self.push(Function(code, None, defaults, closure, self))

    def byte_GET_ITER(self):
        self.push(iter(self.pop()))

    def byte_FOR_ITER(self, jump):
        iterobj = self.pop()
        self.push(iterobj)
        #if not isinstance(iterobj, (Class, Object): # these are unsafe
                                                     # i.e. defined by user
        try:
            v = iterobj.next()
            self.push(v)
        except StopIteration:
            self.pop()
            self.frame().f_lasti = jump

if __name__ == "__main__":
    trialCode = """
from __future__ import generators
import os
assert os
print os.getcwd()

def generator():
    for i in xrange(5):
        yield (i*2)

#for i in generator():
#    print i

def makeAdder(base):
    def adder(x):
        return base + x
    return adder

add5 = makeAdder(5)
assert add5(6) == 11

class Foo:
    x = 1
    def __init__(self, y):
        self.y = y
    def add(self, z):
        return self.x + self.y + z

f = Foo(2)
assert f.add(3) == 6
assert Foo.add(f, 4) == 7

try:
    [][1]
    assert 0, "should have raised index error"
except IndexError:
    pass

try:
    try:
        [][1]
        assert 0, "should have hit finally"
    finally:
        pass
    assert 0, "should have hit except"
except:
    pass

try:
    f = 1
finally:
    f = 2
assert f == 2
"""

    codeObject = compile(trialCode, '<input>', 'exec')
    vm = VirtualMachine()
    vm.loadCode(codeObject)
    vm.run()

    def inputCodeObject():
        c = ''
        i = raw_input('>>> ')
        try:
            codeObject = compile(i, '<input>', 'eval')
            return codeObject
        except:
            try:
                codeObject = compile(i, '<input>', 'exec')
                return codeObject
            except SyntaxError, e:
                if not c and str(e).startswith('unexpected EOF'):
                    c = i+'\n'
                else:
                    raise
        while 1:
            i = raw_input('... ')
            if i:
                c += '%s\n' % i
            else:
                break
        return compile(c, '<input>', 'exec')
            
    
    while 1:
        try:
            codeObject = inputCodeObject()
            vm.loadCode(codeObject)
            val = vm.run()
            if val != None:
                print val
        except EOFError:
            break
        except KeyboardInterrupt:
            print "KeyboardInterrupt"
        except:
            import traceback
            traceback.print_exc()
