# optimizer.py
# CS4031 - Compiler Construction | Fall 2025
#
# Implementation of basic optimizations on TACKY IR:
# 1. Constant Folding - evaluate constant expressions at compile time
# 2. Dead Store Elimination - remove assignments to unused variables
# 3. Algebraic Simplification - apply algebraic identities
# 4. Strength Reduction - replace expensive operations with cheaper ones

from typing import List, Dict, Set, Tuple, Optional
from src.backend.ir.tacky import *
from src.frontend.parser._ast5 import Int, Long, UInt, ULong, Double


class OptimizationStats:
    """Track statistics about optimizations performed."""
    def __init__(self):
        self.constants_folded = 0
        self.dead_stores_eliminated = 0
        self.algebraic_simplifications = 0
        self.strength_reductions = 0
        self.total_instructions_before = 0
        self.total_instructions_after = 0

    def __repr__(self):
        return (
            f"OptimizationStats(\n"
            f"  constants_folded={self.constants_folded},\n"
            f"  dead_stores_eliminated={self.dead_stores_eliminated},\n"
            f"  algebraic_simplifications={self.algebraic_simplifications},\n"
            f"  strength_reductions={self.strength_reductions},\n"
            f"  instructions: {self.total_instructions_before} -> {self.total_instructions_after}\n"
            f")"
        )


def is_constant(val) -> bool:
    """Check if a value is a constant."""
    return isinstance(val, TackyConstant)


def get_constant_value(val) -> Optional[int]:
    """Extract numeric value from a TackyConstant."""
    if isinstance(val, TackyConstant):
        const = val.value
        # Handle different constant types
        if hasattr(const, '_int'):
            return const._int
        elif hasattr(const, 'value'):
            return const.value
        elif isinstance(const, (int, float)):
            return const
    return None


def make_constant(value: int, original_type=None) -> TackyConstant:
    """Create a TackyConstant with the given value."""
    from src.frontend.parser._ast5 import ConstInt, ConstLong

    # Determine appropriate type based on value size
    if abs(value) > 2**31 - 1:
        return TackyConstant(ConstLong(value))
    else:
        return TackyConstant(ConstInt(value))


def evaluate_binary_op(op: str, left: int, right: int) -> Optional[int]:
    """Evaluate a binary operation on two constant values."""
    try:
        if op == 'Add':
            return left + right
        elif op == 'Subtract':
            return left - right
        elif op == 'Multiply':
            return left * right
        elif op == 'Divide':
            if right == 0:
                return None  # Can't fold division by zero
            return left // right
        elif op == 'Remainder':
            if right == 0:
                return None
            return left % right
        elif op == 'Equal':
            return 1 if left == right else 0
        elif op == 'NotEqual':
            return 1 if left != right else 0
        elif op == 'LessThan':
            return 1 if left < right else 0
        elif op == 'LessOrEqual':
            return 1 if left <= right else 0
        elif op == 'GreaterThan':
            return 1 if left > right else 0
        elif op == 'GreaterOrEqual':
            return 1 if left >= right else 0
        elif op == 'And':
            return 1 if (left and right) else 0
        elif op == 'Or':
            return 1 if (left or right) else 0
    except:
        pass
    return None


def evaluate_unary_op(op: str, val: int) -> Optional[int]:
    """Evaluate a unary operation on a constant value."""
    try:
        if op == 'Negation' or op == 'Negate':
            return -val
        elif op == 'Complement':
            return ~val
        elif op == 'Not':
            return 1 if val == 0 else 0
    except:
        pass
    return None


# =============================================================================
# CONSTANT FOLDING
# =============================================================================

def constant_folding(instructions: List[TackyInstruction], stats: OptimizationStats) -> List[TackyInstruction]:
    """
    Constant Folding: Evaluate constant expressions at compile time.

    Before: tmp.1 = 3 + 5
    After:  tmp.1 = 8
    """
    result = []

    # Track known constant values for propagation
    known_constants: Dict[str, int] = {}

    for instr in instructions:
        if isinstance(instr, TackyBinary):
            # Try to get constant values (either direct or propagated)
            left_val = get_constant_value(instr.src1)
            right_val = get_constant_value(instr.src2)

            # Check if operands are known constants (propagation)
            if left_val is None and isinstance(instr.src1, TackyVar):
                var_name = instr.src1.identifier
                if var_name in known_constants:
                    left_val = known_constants[var_name]

            if right_val is None and isinstance(instr.src2, TackyVar):
                var_name = instr.src2.identifier
                if var_name in known_constants:
                    right_val = known_constants[var_name]

            # If both operands are constants, fold them
            if left_val is not None and right_val is not None:
                folded = evaluate_binary_op(instr.operator, left_val, right_val)
                if folded is not None:
                    # Replace with Copy instruction
                    new_const = make_constant(folded)
                    result.append(TackyCopy(new_const, instr.dst))

                    # Track the result as a known constant
                    if isinstance(instr.dst, TackyVar):
                        known_constants[instr.dst.identifier] = folded

                    stats.constants_folded += 1
                    continue

            result.append(instr)

        elif isinstance(instr, TackyUnary):
            # Try to fold unary operations on constants
            src_val = get_constant_value(instr.src)

            if src_val is None and isinstance(instr.src, TackyVar):
                var_name = instr.src.identifier
                if var_name in known_constants:
                    src_val = known_constants[var_name]

            if src_val is not None:
                folded = evaluate_unary_op(instr.operator, src_val)
                if folded is not None:
                    new_const = make_constant(folded)
                    result.append(TackyCopy(new_const, instr.dst))

                    if isinstance(instr.dst, TackyVar):
                        known_constants[instr.dst.identifier] = folded

                    stats.constants_folded += 1
                    continue

            result.append(instr)

        elif isinstance(instr, TackyCopy):
            # Track constant copies for propagation
            src_val = get_constant_value(instr.src)
            if src_val is not None and isinstance(instr.dst, TackyVar):
                known_constants[instr.dst.identifier] = src_val
            elif isinstance(instr.src, TackyVar) and instr.src.identifier in known_constants:
                if isinstance(instr.dst, TackyVar):
                    known_constants[instr.dst.identifier] = known_constants[instr.src.identifier]

            result.append(instr)

        else:
            # Labels, jumps, function calls, etc. invalidate our knowledge
            if isinstance(instr, (TackyLabel, TackyJump, TackyJumpIfZero, TackyJumpIfNotZero, TackyFunCall)):
                known_constants.clear()
            result.append(instr)

    return result


# =============================================================================
# ALGEBRAIC SIMPLIFICATION
# =============================================================================

def algebraic_simplification(instructions: List[TackyInstruction], stats: OptimizationStats) -> List[TackyInstruction]:
    """
    Algebraic Simplification: Apply algebraic identities.

    x + 0 = x,  x - 0 = x,  x * 1 = x,  x * 0 = 0,  x / 1 = x
    """
    result = []

    for instr in instructions:
        if isinstance(instr, TackyBinary):
            left_val = get_constant_value(instr.src1)
            right_val = get_constant_value(instr.src2)
            op = instr.operator

            simplified = False

            # x + 0 = x
            if op == 'Add' and right_val == 0:
                result.append(TackyCopy(instr.src1, instr.dst))
                simplified = True
            # 0 + x = x
            elif op == 'Add' and left_val == 0:
                result.append(TackyCopy(instr.src2, instr.dst))
                simplified = True
            # x - 0 = x
            elif op == 'Subtract' and right_val == 0:
                result.append(TackyCopy(instr.src1, instr.dst))
                simplified = True
            # x * 1 = x
            elif op == 'Multiply' and right_val == 1:
                result.append(TackyCopy(instr.src1, instr.dst))
                simplified = True
            # 1 * x = x
            elif op == 'Multiply' and left_val == 1:
                result.append(TackyCopy(instr.src2, instr.dst))
                simplified = True
            # x * 0 = 0
            elif op == 'Multiply' and (right_val == 0 or left_val == 0):
                result.append(TackyCopy(make_constant(0), instr.dst))
                simplified = True
            # x / 1 = x
            elif op == 'Divide' and right_val == 1:
                result.append(TackyCopy(instr.src1, instr.dst))
                simplified = True
            # x % 1 = 0 (for positive x)
            elif op == 'Remainder' and right_val == 1:
                result.append(TackyCopy(make_constant(0), instr.dst))
                simplified = True
            # x && 0 = 0
            elif op == 'And' and (right_val == 0 or left_val == 0):
                result.append(TackyCopy(make_constant(0), instr.dst))
                simplified = True
            # x || 1 = 1
            elif op == 'Or' and (right_val == 1 or left_val == 1):
                result.append(TackyCopy(make_constant(1), instr.dst))
                simplified = True

            if simplified:
                stats.algebraic_simplifications += 1
            else:
                result.append(instr)
        else:
            result.append(instr)

    return result


# =============================================================================
# STRENGTH REDUCTION
# =============================================================================

def strength_reduction(instructions: List[TackyInstruction], stats: OptimizationStats) -> List[TackyInstruction]:
    """
    Strength Reduction: Replace expensive operations with cheaper equivalents.

    x * 2 -> x + x (or x << 1)
    x * 4 -> x << 2
    x / 2 -> x >> 1 (for unsigned)
    x % 2 -> x & 1
    """
    result = []

    for instr in instructions:
        if isinstance(instr, TackyBinary):
            right_val = get_constant_value(instr.src2)
            op = instr.operator

            reduced = False

            # x * 2 -> x + x
            if op == 'Multiply' and right_val == 2:
                result.append(TackyBinary('Add', instr.src1, instr.src1, instr.dst))
                reduced = True
            # x % 2 -> x & 1 (bitwise AND)
            # Note: We keep it as modulo since we don't have bitwise AND in TACKY
            # This would be applied at assembly level

            if reduced:
                stats.strength_reductions += 1
            else:
                result.append(instr)
        else:
            result.append(instr)

    return result


# =============================================================================
# DEAD STORE ELIMINATION
# =============================================================================

def get_defined_var(instr: TackyInstruction) -> Optional[str]:
    """Get the variable defined by an instruction, if any."""
    if isinstance(instr, (TackyBinary, TackyUnary, TackyCopy, TackySignExtend,
                         TackyTruncate, TackyZeroExtend, TackyLoad, TackyGetAddress,
                         TackyFunCall, TackyAddPtr)):
        if hasattr(instr, 'dst') and isinstance(instr.dst, TackyVar):
            return instr.dst.identifier
    return None


def get_used_vars(instr: TackyInstruction) -> Set[str]:
    """Get all variables used (read) by an instruction."""
    used = set()

    if isinstance(instr, TackyBinary):
        if isinstance(instr.src1, TackyVar):
            used.add(instr.src1.identifier)
        if isinstance(instr.src2, TackyVar):
            used.add(instr.src2.identifier)
    elif isinstance(instr, TackyUnary):
        if isinstance(instr.src, TackyVar):
            used.add(instr.src.identifier)
    elif isinstance(instr, TackyCopy):
        if isinstance(instr.src, TackyVar):
            used.add(instr.src.identifier)
    elif isinstance(instr, TackyReturn):
        if isinstance(instr.val, TackyVar):
            used.add(instr.val.identifier)
    elif isinstance(instr, (TackyJumpIfZero, TackyJumpIfNotZero)):
        if isinstance(instr.condition, TackyVar):
            used.add(instr.condition.identifier)
    elif isinstance(instr, TackyFunCall):
        for arg in instr.args:
            if isinstance(arg, TackyVar):
                used.add(arg.identifier)
    elif isinstance(instr, TackyStore):
        if isinstance(instr.src, TackyVar):
            used.add(instr.src.identifier)
        if isinstance(instr.dst_ptr, TackyVar):
            used.add(instr.dst_ptr.identifier)
    elif isinstance(instr, TackyLoad):
        if isinstance(instr.src_ptr, TackyVar):
            used.add(instr.src_ptr.identifier)
    elif isinstance(instr, (TackySignExtend, TackyTruncate, TackyZeroExtend)):
        if isinstance(instr.src, TackyVar):
            used.add(instr.src.identifier)
    elif isinstance(instr, TackyAddPtr):
        if isinstance(instr.ptr, TackyVar):
            used.add(instr.ptr.identifier)
        if isinstance(instr.index, TackyVar):
            used.add(instr.index.identifier)
    elif isinstance(instr, TackyCopyToOffSet):
        if isinstance(instr.src, TackyVar):
            used.add(instr.src.identifier)
    elif isinstance(instr, TackyCopyFromOffSet):
        if isinstance(instr.src, TackyVar):
            used.add(instr.src.identifier)

    return used


def dead_store_elimination(instructions: List[TackyInstruction], stats: OptimizationStats) -> List[TackyInstruction]:
    """
    Dead Store Elimination: Remove assignments to variables that are never read.

    Uses backward dataflow analysis to find live variables.
    """
    if not instructions:
        return instructions

    # Build list of (instruction_index, defined_var, used_vars)
    n = len(instructions)

    # Compute live variables using backward analysis
    # A variable is live at a point if it may be read before being written

    live_out: List[Set[str]] = [set() for _ in range(n)]
    live_in: List[Set[str]] = [set() for _ in range(n)]

    # Simple backward pass - iterate until fixed point
    changed = True
    iterations = 0
    max_iterations = 100  # Prevent infinite loops

    while changed and iterations < max_iterations:
        changed = False
        iterations += 1

        for i in range(n - 1, -1, -1):
            instr = instructions[i]

            # live_out[i] = union of live_in of successors
            # For simplicity, assume linear flow (successor is i+1)
            # Jumps would need CFG analysis
            old_live_out = live_out[i].copy()

            if i + 1 < n:
                live_out[i] = live_in[i + 1].copy()
            else:
                live_out[i] = set()

            # For jump targets, we'd need to add their live_in too
            # (simplified: we keep all non-tmp variables as potentially live)

            # live_in[i] = used[i] ∪ (live_out[i] - defined[i])
            old_live_in = live_in[i].copy()

            defined = get_defined_var(instr)
            used = get_used_vars(instr)

            live_in[i] = used.copy()
            for var in live_out[i]:
                if var != defined:
                    live_in[i].add(var)

            if live_in[i] != old_live_in or live_out[i] != old_live_out:
                changed = True

    # Now eliminate dead stores
    result = []
    for i, instr in enumerate(instructions):
        defined = get_defined_var(instr)

        # Keep instruction if:
        # 1. It doesn't define a variable (labels, jumps, returns, etc.)
        # 2. The defined variable is live out
        # 3. It's a function call (may have side effects)
        # 4. It's a store (may have side effects)
        # 5. It defines a non-temporary variable (conservative: might be used elsewhere)

        if defined is None:
            result.append(instr)
        elif isinstance(instr, (TackyFunCall, TackyStore, TackyCopyToOffSet)):
            result.append(instr)
        elif not defined.startswith('tmp.'):
            # Non-temporary variables might be used after function returns
            result.append(instr)
        elif defined in live_out[i]:
            result.append(instr)
        else:
            # Dead store - eliminate it
            stats.dead_stores_eliminated += 1

    return result


# =============================================================================
# MAIN OPTIMIZATION FUNCTION
# =============================================================================

def optimize_function(func: TackyFunction, stats: OptimizationStats) -> TackyFunction:
    """Apply all optimizations to a function."""
    instructions = func.body

    # Apply optimizations in order
    # Run multiple passes for better results
    for _ in range(3):  # Multiple passes
        old_len = len(instructions)

        instructions = constant_folding(instructions, stats)
        instructions = algebraic_simplification(instructions, stats)
        instructions = strength_reduction(instructions, stats)
        instructions = dead_store_elimination(instructions, stats)

        # If no changes, stop iterating
        if len(instructions) == old_len:
            break

    # Create new function with optimized body
    return TackyFunction(
        identifier=func.name,
        _global=func._global,
        params=func.params,
        body=instructions
    )


def optimize_program(program: TackyProgram, enabled: bool = True) -> Tuple[TackyProgram, OptimizationStats]:
    """
    Apply optimizations to an entire TACKY program.

    Args:
        program: The TACKY IR program to optimize
        enabled: If False, skip optimization and return original program

    Returns:
        Tuple of (optimized program, statistics)
    """
    stats = OptimizationStats()

    if not enabled:
        return program, stats

    # Count instructions before optimization
    for item in program.function_definition:
        if isinstance(item, TackyFunction):
            stats.total_instructions_before += len(item.body)

    # Optimize each function
    optimized_items = []
    for item in program.function_definition:
        if isinstance(item, TackyFunction):
            optimized_func = optimize_function(item, stats)
            optimized_items.append(optimized_func)
            stats.total_instructions_after += len(optimized_func.body)
        else:
            # Static variables, constants - pass through unchanged
            optimized_items.append(item)

    return TackyProgram(optimized_items), stats
