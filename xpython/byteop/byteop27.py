"""Byte Interpreter operations for Python 2.7
"""
class ByteOp27():
    def __init__(self, vm):
        self.vm = vm

    # Order of function here is the same as in:
    # https://docs.python.org/2.7/library/dis.html#python-bytecode-instructions


    def NOP(self):
        "Do nothing code. Used as a placeholder by the bytecode optimizer."
        pass

    def POP_TOP(self):
        "Removes the top-of-stack (TOS) item."
        self.vm.pop()

    def ROT_TWO(self):
        "Swaps the two top-most stack items."
        a, b = self.vm.popn(2)
        self.vm.push(b, a)

    def ROT_THREE(self):
        "Lifts second and third stack item one position up, moves top down to position three."
        a, b, c = self.vm.popn(3)
        self.vm.push(c, a, b)

    def ROT_FOUR(self):
        "Lifts second, third and forth stack item one position up, moves top down to position four."
        a, b, c, d = self.vm.popn(4)
        self.vm.push(d, a, b, c)

    def DUP_TOP(self):
        "Duplicates the reference on top of the stack."
        self.vm.push(self.vm.top())

    def LOAD_CONST(self, const):
        self.vm.push(const)

    def LOAD_NAME(self, name):
        frame = self.vm.frame
        if name in frame.f_locals:
            val = frame.f_locals[name]
        elif name in frame.f_globals:
            val = frame.f_globals[name]
        elif name in frame.f_builtins:
            val = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        self.vm.push(val)

    def DUP_TOPX(self, count):
        items = self.vm.popn(count)
        for i in [1, 2]:
            self.vm.push(*items)
