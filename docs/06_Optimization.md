# Optimization Documentation

## CS4031 - Compiler Construction | Fall 2025

---

## 1. Overview

The optimization phase improves the generated code for efficiency without changing program semantics. The Mini-C compiler implements several basic optimizations.

**Location:** Various files in `src/backend/`

---

## 2. Implemented Optimizations

### 2.1 Constant Folding

**Description:** Evaluate constant expressions at compile time.

**Before:**
```
tmp.1 = 3 + 5
tmp.2 = tmp.1 * 2
x = tmp.2
```

**After:**
```
x = 16
```

**Implementation:**
```python
def fold_constants(instruction):
    if isinstance(instruction, Binary):
        if is_constant(instruction.left) and is_constant(instruction.right):
            result = evaluate(instruction.op,
                            instruction.left.value,
                            instruction.right.value)
            return Copy(src=Constant(result), dst=instruction.dst)
    return instruction
```

**Supported Operations:**
| Operation | Example | Result |
|-----------|---------|--------|
| Addition | `3 + 5` | `8` |
| Subtraction | `10 - 3` | `7` |
| Multiplication | `4 * 5` | `20` |
| Division | `20 / 4` | `5` |
| Remainder | `17 % 5` | `2` |
| Comparison | `5 < 10` | `1` |
| Logical AND | `1 && 1` | `1` |
| Logical OR | `0 \|\| 1` | `1` |

---

### 2.2 Cast Simplification

**Description:** Remove unnecessary type casts.

**Before:**
```
tmp.1 = (int) x      ; x is already int
tmp.2 = (long) tmp.1
tmp.3 = (long) y     ; y is int, cast to long
tmp.4 = tmp.2 + tmp.3
```

**After:**
```
tmp.2 = (long) x     ; Single cast
tmp.3 = (long) y
tmp.4 = tmp.2 + tmp.3
```

**Rules:**
1. Remove cast if source and target types are identical
2. Combine consecutive casts when possible
3. Remove casts that don't change value (e.g., int to long for small values)

---

### 2.3 Dead Store Elimination

**Description:** Remove assignments to variables that are never read.

**Before:**
```
x = 5          ; x assigned
x = 10         ; x reassigned before use - first assignment is dead
y = x + 1
```

**After:**
```
x = 10
y = x + 1
```

**Algorithm:**
```python
def eliminate_dead_stores(instructions):
    # Build use-def chains
    live_vars = compute_live_variables(instructions)

    result = []
    for instr in reversed(instructions):
        if isinstance(instr, Copy) or isinstance(instr, Binary):
            # If destination is not live, skip this instruction
            if instr.dst not in live_vars:
                continue
        result.append(instr)

    return reversed(result)
```

---

### 2.4 Strength Reduction

**Description:** Replace expensive operations with cheaper equivalents.

| Original | Optimized | Reason |
|----------|-----------|--------|
| `x * 2` | `x + x` or `x << 1` | Shift is faster |
| `x * 4` | `x << 2` | Shift is faster |
| `x / 2` | `x >> 1` (unsigned) | Shift is faster |
| `x % 2` | `x & 1` | Bitwise is faster |

---

### 2.5 Algebraic Simplification

**Description:** Apply algebraic identities to simplify expressions.

| Pattern | Simplified |
|---------|------------|
| `x + 0` | `x` |
| `x - 0` | `x` |
| `x * 1` | `x` |
| `x * 0` | `0` |
| `x / 1` | `x` |
| `x - x` | `0` |
| `x && 1` | `x` (if boolean) |
| `x \|\| 0` | `x` (if boolean) |

---

## 3. Optimization Examples

### Example 1: Arithmetic Simplification

**Source:**
```c
int f(int x) {
    int a = x + 0;
    int b = a * 1;
    int c = b * 2;
    return c + (10 - 10);
}
```

**Before Optimization (TACKY IR):**
```
tmp.1 = x + 0
a = tmp.1
tmp.2 = a * 1
b = tmp.2
tmp.3 = b * 2
c = tmp.3
tmp.4 = 10 - 10
tmp.5 = c + tmp.4
return tmp.5
```

**After Optimization:**
```
tmp.3 = x << 1    ; x * 2 strength reduced to shift
return tmp.3      ; All identity operations eliminated
```

### Example 2: Dead Code and Constant Folding

**Source:**
```c
int f(void) {
    int x = 5;
    int y = 10;
    int z = x + y;    // Constant expression
    int unused = 100; // Dead store
    return z;
}
```

**Before Optimization:**
```
x = 5
y = 10
tmp.1 = x + y
z = tmp.1
unused = 100
return z
```

**After Optimization:**
```
return 15         ; Constant folded, dead store eliminated
```

### Example 3: Loop-Invariant Values

**Source:**
```c
int f(int n) {
    int sum = 0;
    int multiplier = 2 * 3;  // Constant
    for (int i = 0; i < n; i = i + 1) {
        sum = sum + i * multiplier;
    }
    return sum;
}
```

**Optimization Applied:**
- `2 * 3` is constant-folded to `6`
- `i * 6` could be strength-reduced in advanced optimizers

---

## 4. Optimization Levels

| Level | Optimizations Applied |
|-------|----------------------|
| O0 (None) | No optimizations |
| O1 (Basic) | Constant folding, dead store elimination |
| O2 (Standard) | O1 + cast simplification, strength reduction |

*Note: The Mini-C compiler primarily implements O1-level optimizations.*

---

## 5. Optimization Pass Order

```
1. Constant Folding
   ↓
2. Algebraic Simplification
   ↓
3. Cast Simplification
   ↓
4. Dead Store Elimination
   ↓
5. Strength Reduction
```

The order matters because:
- Constant folding may create opportunities for algebraic simplification
- Algebraic simplification may create dead stores
- All earlier passes may create opportunities for dead store elimination

---

## 6. Limitations

The Mini-C compiler does **not** implement these advanced optimizations:

| Optimization | Description |
|--------------|-------------|
| Loop Unrolling | Replicate loop body |
| Function Inlining | Replace call with body |
| Common Subexpression Elimination | Reuse computed values |
| Loop-Invariant Code Motion | Move computations out of loops |
| Register Allocation Optimization | Minimize spills |
| Tail Call Optimization | Convert tail recursion to loops |

These are left as potential future enhancements.

---

## 7. Measuring Optimization Impact

### Metrics:
- **Instruction Count**: Fewer instructions = faster
- **Memory Operations**: Fewer loads/stores = faster
- **Branch Count**: Fewer jumps = better pipeline

### Example Comparison:

| Metric | Before Opt | After Opt | Improvement |
|--------|------------|-----------|-------------|
| Instructions | 12 | 5 | 58% fewer |
| Memory Ops | 8 | 2 | 75% fewer |
| Temporaries | 6 | 2 | 67% fewer |

---

*This document describes the optimization phase of the Mini-C compiler.*
