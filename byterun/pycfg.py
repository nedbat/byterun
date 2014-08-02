"""Build a Control Flow Graph (CFG) from CPython bytecode.

A class that builds and provides access to a CFG built from CPython bytecode.

For a basic introduction to CFGs see the wikipedia article:
http://en.wikipedia.org/wiki/Control_flow_graph
"""

import bisect
import dis
import itertools
import logging


import six

PY3, PY2 = six.PY3, not six.PY3

if six.PY3:
  byteint = lambda b: b
else:
  byteint = ord

log = logging.getLogger(__name__)

# The following sets contain instructions with specific branching properties.

# Untargetted unconditional jumps always jump, but do so to some statically
# unknown location. Examples include, raising exceptions and returning from
# functions: in both cases you are jumping but you cannot statically determine
# to where.
_UNTARGETTED_UNCONDITIONAL_JUMPS = frozenset([
    dis.opmap["BREAK_LOOP"],
    dis.opmap["RETURN_VALUE"],
    dis.opmap["RAISE_VARARGS"],
    ])

# Untargetted conditional jumps may jump to a statically unknown location, but
# may allow control to continue to the next instruction.
_UNTARGETTED_CONDITIONAL_JUMPS = frozenset([
    dis.opmap["END_FINALLY"],
    dis.opmap["EXEC_STMT"],
    dis.opmap["WITH_CLEANUP"],
    dis.opmap["IMPORT_NAME"],
    dis.opmap["IMPORT_FROM"],
    dis.opmap["IMPORT_STAR"],
    dis.opmap["CALL_FUNCTION"],
    dis.opmap["CALL_FUNCTION_VAR"],
    dis.opmap["CALL_FUNCTION_KW"],
    dis.opmap["CALL_FUNCTION_VAR_KW"],
    dis.opmap["YIELD_VALUE"],  # yield is treated as both branching somewhere
                               # unknown and to the next instruction.
    ])

# Targetted unconditional jumps always jump to a statically known target
# instruction.
_TARGETTED_UNCONDITIONAL_JUMPS = frozenset([
    dis.opmap["CONTINUE_LOOP"],
    dis.opmap["JUMP_FORWARD"],
    dis.opmap["JUMP_ABSOLUTE"],
    ])

# Targetted conditional jumps either jump to a statically known target or they
# continue to the next instruction.
_TARGETTED_CONDITIONAL_JUMPS = frozenset([
    dis.opmap["POP_JUMP_IF_TRUE"],
    dis.opmap["POP_JUMP_IF_FALSE"],
    dis.opmap["JUMP_IF_TRUE_OR_POP"],
    dis.opmap["JUMP_IF_FALSE_OR_POP"],
    dis.opmap["FOR_ITER"],
    ])

_TARGETTED_JUMPS = (_TARGETTED_CONDITIONAL_JUMPS |
                    _TARGETTED_UNCONDITIONAL_JUMPS)

_CONDITIONAL_JUMPS = (_TARGETTED_CONDITIONAL_JUMPS |
                      _UNTARGETTED_CONDITIONAL_JUMPS)

_UNTARGETTED_JUMPS = (_UNTARGETTED_CONDITIONAL_JUMPS |
                      _UNTARGETTED_UNCONDITIONAL_JUMPS)


def _parse_instructions(code):
  """A generator yielding each instruction in code.

  Args:
    code: A bytecode string (not a code object).

  Yields:
    A triple (opcode, argument or None, offset) for each instruction in code.
    Where offset is the byte offset of the beginning of the instruction.

  This is derived from dis.findlabels in the Python standard library.
  """
  n = len(code)
  i = 0
  while i < n:
    offset = i
    op = byteint(code[i])
    i += 1
    oparg = None
    if op >= dis.HAVE_ARGUMENT:
      oparg = byteint(code[i]) + byteint(code[i+1])*256
      i += 2
    yield (op, oparg, offset)


class InstructionsIndex(object):
  """An index of all the instructions in a code object.

  Attributes:
    instruction_offsets: A list of instruction offsets.
  """

  def __init__(self, code):
    self.instruction_offsets = [i for _, _, i in _parse_instructions(code)]

  def prev(self, offset):
    """Return the offset of the previous instruction.

    Args:
      offset: The offset of an instruction in the code.

    Returns:
      The offset of the instruction immediately before the instruction specified
      by the offset argument.

    Raises:
      IndexError: If the offset is outside the range of valid instructions.
    """
    if offset < 0:
      raise IndexError("Instruction offset cannot be less than 0")
    if offset > self.instruction_offsets[-1]:
      raise IndexError("Instruction offset cannot be greater than "
                       "the offset of the last instruction")
    # Find the rightmost instruction offset that is less than the offset
    # argument, this will be the previous instruction because it is closest
    # instruction that is before the offset.
    return self.instruction_offsets[
        bisect.bisect_left(self.instruction_offsets, offset) - 1]

  def next(self, offset):
    """Return the offset of the next instruction.

    Args:
      offset: The offset of an instruction in the code.

    Returns:
      The offset of the instruction immediately after the instruction specified
      by the offset argument.

    Raises:
      IndexError: If the offset is outside the range of valid instructions.
    """
    if offset < 0:
      raise IndexError("Instruction offset cannot be less than 0")
    if offset > self.instruction_offsets[-1]:
      raise IndexError("Instruction offset cannot be greater than "
                       "the offset of the last instruction")
    # Find the leftmost instruction offset that is greater than the offset
    # argument, this will be the next instruction because it is closest
    # instruction that is after the offset.
    return self.instruction_offsets[
        bisect.bisect_right(self.instruction_offsets, offset)]


def _find_jumps(code):
  """Detect all offsets in a byte code which are instructions that can jump.

  Args:
    code: A bytecode string (not a code object).

  Returns:
    A pair of a dict and set. The dict mapping the offsets of jump instructions
    to sets with the same semantics as outgoing in Block. The set of all the
    jump targets it found.
  """
  all_targets = set()
  jumps = {}
  for op, oparg, i in _parse_instructions(code):
    targets = set()
    is_jump = False
    next_i = i + 1 if oparg is None else i + 3
    if oparg is not None:
      if op in _TARGETTED_JUMPS:
        # Add the known jump target
        is_jump = True
        if op in dis.hasjrel:
          targets.add(next_i+oparg)
          all_targets.add(next_i+oparg)
        elif op in dis.hasjabs:
          targets.add(oparg)
          all_targets.add(oparg)
        else:
          targets.add(None)

    if op in _CONDITIONAL_JUMPS:
      # The jump is conditional so add the next instruction as a target
      is_jump = True
      targets.add(next_i)
      all_targets.add(next_i)
    if op in _UNTARGETTED_JUMPS:
      # The jump is untargetted so add None to mean unknown target
      is_jump = True
      targets.add(None)

    if is_jump:
      jumps[i] = targets
  return jumps, all_targets


class Block(object):
  """A Block instance represents a basic block in the CFG.

  Each basic block has at most one jump instruction which is always at the
  end. In this representation we will not add forward jumps to blocks that don't
  have them and instead just take a block that has no jump instruction as
  implicitly jumping to the next instruction when it reaches the end of the
  block. Control may only jump to the beginning of a basic block, so if any
  instruction in a basic block executes they all do and they do so in order.

  Attributes:

    begin, end: The beginning and ending (resp) offsets of the basic block in
                bytes.

    outgoing: A set of blocks that the last instruction of this basic block can
              branch to. A None in this set denotes that there are statically
              unknown branch targets (due to exceptions, for instance).

    incoming: A set of blocks that can branch to the beginning of this
              basic block.

    code: The code object that contains this basic block.

  This object uses the identity hash and equality. This is correct as there
  should never be more than one block object that represents the same actual
  basic block.
  """

  def __init__(self, begin, end, code, block_table):
    self.outgoing = set()
    self.incoming = set()
    self._dominators = set()
    self._reachable_from = None
    self.begin = begin
    self.end = end
    self.code = code
    self.block_table = block_table

  def reachable_from(self, other):
    """Return true if self is reachable from other.

    Args:
      other: A block.

    Returns:
      A boolean
    """
    return other in self._reachable_from

  def dominates(self, other):
    """Return true if self dominates other.

    Args:
      other: A block.

    Returns:
      A boolean
    """
    # This is an instance of my own class and this inversion makes the interface
    # cleaner
    # pylint: disable=protected-access
    return self in other._dominators

  def get_name(self):
    return "{}:{}-{}".format(self.block_table.get_filename(),
                             self.block_table.get_line(self.begin),
                             self.block_table.get_line(self.end))

  def __repr__(self):
    return "{}(outgoing={{{}}},incoming={{{}}})".format(
        self.get_name(),
        ", ".join(b.get_name() for b in self.outgoing),
        ", ".join(b.get_name() for b in self.incoming))


class BlockTable(object):
  """A table of basic blocks in a single bytecode object.

  A None in an outgoing list means that that block can branch to an unknown
  location (usually by returning or raising an exception). At the moment,
  continue and break are also treated this way, however it will be possible to
  remove them as the static target is known from the enclosing SETUP_LOOP
  instruction.

  The algorithm to build the Control Flow Graph (CFG) is the naive algorithm
  presented in many compilers classes and probably most compiler text books. We
  simply find all the instructions where CFGs end and begin, make sure they
  match up (there is a begin after every end), and then build a basic block for
  ever range between a beginning and an end. This may not produce the smallest
  possible CFG, but it will produce a correct one because every branch point
  becomes the end of a basic block and every instruction that is branched to
  becomes the beginning of a basic block.
  """

  def __init__(self, code):
    """Construct a table with the blocks in the given code object.

    Args:
      code: a code object (such as function.func_code) to process.
    """
    self.code = code
    self.line_offsets, self.lines = zip(*dis.findlinestarts(self.code))

    instruction_index = InstructionsIndex(code.co_code)

    # Get a map from jump instructions to jump targets and a combined set of all
    # targets.
    jumps, all_targets = _find_jumps(code.co_code)

    # TODO(ampere): Using dis.findlabels may not be the right
    # thing. Specifically it is not clear when the targets of SETUP_*
    # instructions should be used to make basic blocks.

    # Make a list of all the directly obvious block begins from the jump targets
    # found above and the labels found by dis.
    direct_begins = all_targets.union(dis.findlabels(code.co_code))

    # Any jump instruction must be the end of a basic block.
    direct_ends = jumps.viewkeys()

    # The actual sorted list of begins is build using the direct_begins along
    # with all instructions that follow a jump instruction. Also the beginning
    # of the code is a begin.
    begins = [0] + sorted(set(list(direct_begins) +
                              [instruction_index.next(i) for i in direct_ends
                               if i < len(code.co_code) - 1]))
    # The actual ends are every instruction that proceeds a real block begin and
    # the last instruction in the code. Since we included the instruction after
    # every jump above this will include every jump and every instruction that
    # comes before a target.
    ends = ([instruction_index.prev(i) for i in begins if i > 0] +
            [instruction_index.instruction_offsets[-1]])

    # Add targets for the ends of basic blocks that don't have a real jump
    # instruction.
    for end in ends:
      if end not in jumps:
        jumps[end] = set([instruction_index.next(end)])

    # Build a reverse mapping from jump targets to the instructions that jump to
    # them.
    reversemap = {0: set()}
    for (jump, targets) in jumps.items():
      for target in targets:
        reversemap.setdefault(target, set()).add(jump)
    for begin in begins:
      if begin not in reversemap:
        reversemap[begin] = set()

    assert len(begins) == len(ends)

    # Build the actual basic blocks by pairing the begins and ends directly.
    self._blocks = [Block(begin, end, code=code, block_table=self)
                    for begin, end in itertools.izip(begins, ends)]
    # Build a begins list for use with bisect
    self._block_begins = [b.begin for b in self._blocks]
    # Fill in incoming and outgoing
    for block in self._blocks:
      block.outgoing = frozenset(self.get_basic_block(o) if
                                 o is not None else None
                                 for o in jumps[block.end])
      block.incoming = frozenset(self.get_basic_block(o)
                                 for o in reversemap[block.begin])
    # TODO(ampere): Both _dominators and _reachable_from are O(n^2) where n is
    # the number of blocks. This could be corrected by using a tree and
    # searching down it for lookups.
    self._compute_dominators()
    # Compute all the reachability information by starting recursion from each
    # node.
    # TODO(ampere): This could be much more efficient, but graphs are small.
    for block in self._blocks:
      if not block.incoming:
        self._compute_reachable_from(block, frozenset())

  def get_basic_block(self, index):
    """Get the basic block that contains the instruction at the given index."""
    return self._blocks[bisect.bisect_right(self._block_begins, index) - 1]

  def get_line(self, index):
    """Get the line number for an instruction.

    Args:
      index: The offset of the instruction.

    Returns:
      The line number of the specified instruction.
    """
    return self.lines[max(bisect.bisect_right(self.line_offsets, index)-1, 0)]

  def get_filename(self):
    """Get the filename of the code object used in this table.

    Returns:
      The string filename.
    """
    return self.code.co_filename

  @staticmethod
  def _compute_reachable_from(current, history):
    """Compute reachability information starting from current.

    The performs a depth first traversal over the graph and adds information to
    Block._reachable_from about what paths reach each node.

    Args:
      current: The current node in the traversal.
      history: A set of nodes that are on the current path to this node.
    """
    orig = current._reachable_from  # pylint: disable=protected-access
    new = history | (orig or set())
    # The base case is that there is no new information, about this node. This
    # comparison is why None is used above; we need to be able to distinguish
    # nodes we have never touched from nodes with an empty reachable_from set.
    if new != orig:
      current._reachable_from = new  # pylint: disable=protected-access
      for child in current.outgoing:
        if child:
          # pylint: disable=protected-access
          BlockTable._compute_reachable_from(child, history | {current})

  def reachable_from(self, a, b):
    """True if the instruction at a is reachable from the instruction at b."""
    block_a = self.get_basic_block(a)
    block_b = self.get_basic_block(b)
    if block_a == block_b:
      return a >= b
    else:
      return block_a.reachable_from(block_b)

  def _compute_dominators(self):
    """Compute dominators for all nodes by iteration.
    """
    # pylint: disable=protected-access
    # For accessing Block._dominators
    entry = self._blocks[0]
    # Initialize dominators for the entry node to itself
    entry._dominators = frozenset([entry])
    # Initialize all other nodes to be dominated by all nodes
    all_blocks_set = frozenset(self._blocks)
    for block in self._blocks[1:]:  # all but entry block
      block._dominators = all_blocks_set
    # Now we perform iteration to solve for the dominators.
    while True:
      # TODO(ampere): use a worklist here. But graphs are small.
      changed = False
      for block in self._blocks[1:]:  # all but entry block
        # Compute new dominator information for block by taking the intersection
        # of the dominators of every incoming block and adding itself.
        new_dominators = all_blocks_set
        for pred in block.incoming:
          new_dominators &= pred._dominators
        new_dominators |= {block}
        # Update only if something changed.
        if new_dominators != block._dominators:
          block._dominators = new_dominators
          changed = True
      # If we did a pass without changing anything exit.
      if not changed:
        break

  def dominates(self, a, b):
    """True if the instruction at a dominates the instruction at b."""
    block_a = self.get_basic_block(a)
    block_b = self.get_basic_block(b)
    if block_a == block_b:
      # if they are in the same block domination is the same as instruction
      # ordering
      return a <= b
    else:
      return block_a.dominates(block_b)

  def get_ancestors_first_traversal(self):
    """Build an ancestors first traversal of the blocks in this table.

    Back edges are detected and handled specially. Specifically, the back edge
    is ignored for blocks in the cycle (allowing the cycle to be processed), but
    we do not allow the blocks after the loop to come before any block in the
    loop.

    Returns:
      A list of blocks in the proper order.
    """
    # TODO(ampere): This assumes all loops are natural. This may be false, but I
    # kinda doubt it. The python compiler is very well behaved.
    order = [self._blocks[0]]
    # A partially processed block has been added to the order, but is part of a
    # loop that has not been fully processed.
    partially_processed = set()
    worklist = list(self._blocks)
    while worklist:
      block = worklist.pop(0)
      # We can process a block if:
      # 1) All forward incoming blocks are in the order
      # 2) All partially processed blocks are reachable from this block
      forward_incoming = set(b for b in block.incoming
                             if not block.dominates(b))
      all_forward_incoming_ordered = forward_incoming.issubset(order)
      # TODO(ampere): Replace forward_incoming in order check with a counter
      # that counts the remaining blocks not in order. Similarly below for
      # incoming.
      all_partially_processed_reachable = all(b.reachable_from(block)
                                              for b in partially_processed)
      if (not all_forward_incoming_ordered or
          not all_partially_processed_reachable):
        continue
      # When a node is processed:
      #   If all incoming blocks (forward and backward) are in the order add to
      #     the order or remove from partially_processed as needed
      #   Otherwise, there are backward incoming blocks that are not in the
      #     order, and we add block to the order and to partially_processed
      # We add children to the work list if we either removed block from
      # partially_processed or added it to order.
      all_incoming_ordered = block.incoming.issubset(order)
      # When adding to the work list remove None outgoing edges since they
      # represent unknown targets that we cannot handle.
      children = filter(None, block.outgoing)
      if all_incoming_ordered:
        if block in partially_processed:
          # block was waiting on a cycle it is part of, but now the cycle is
          # processed.
          partially_processed.remove(block)
          worklist += children
        elif block not in order:
          # block is ready to add and is not in the order.
          order.append(block)
          worklist += children
      elif block not in order:
        # block is not in the order and is part of a cycle.
        partially_processed.add(block)
        order.append(block)
        worklist += children
    return order


class CFG(object):
  """A Control Flow Graph object.

  The CFG may contain any number of code objects, but edges never go between
  code objects.
  """

  def __init__(self):
    """Initialize a CFG object."""
    self._block_tables = {}

  def get_block_table(self, code):
    """Get (building if needed) the BlockTable for a given code object."""
    if code in self._block_tables:
      ret = self._block_tables[code]
    else:
      ret = BlockTable(code)
      self._block_tables[code] = ret
    return ret

  def get_basic_block(self, code, index):
    """Get a basic block by code object and index."""
    blocktable = self.get_block_table(code)
    return blocktable.get_basic_block(index)


def _bytecode_repr(code):
  """Generate a python expression that evaluates to the bytecode.

  Args:
    code: A python code string.
  Returns:
    A human readable and python parsable expression that gives the bytecode.
  """
  ret = []
  for op, oparg, i in _parse_instructions(code):
    sb = "dis.opmap['" + dis.opname[op] + "']"
    if oparg is not None:
      sb += ", " + str(oparg & 255) + ", " + str((oparg >> 8) & 255)
    sb += ",  # " + str(i)
    if oparg is not None:
      if op in dis.hasjrel:
        sb += ", dest=" + str(i+3+oparg)
      elif op in dis.hasjabs:
        sb += ", dest=" + str(oparg)
      else:
        sb += ", arg=" + str(oparg)
    ret.append(sb)
  return "pycfg._list_to_string([\n  " + "\n  ".join(ret) + "\n  ])"


def _list_to_string(lst):
  return "".join(chr(c) for c in lst)
