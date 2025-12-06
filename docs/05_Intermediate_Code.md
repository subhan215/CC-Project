# Intermediate Code Generation Documentation

## CS4031 - Compiler Construction | Fall 2025

---

## 1. Overview

Intermediate Code Generation is the fourth phase of the Mini-C compiler. It transforms the AST into **TACKY IR** (Three-Address Code), a low-level representation that is machine-independent but close to assembly.

**Location:**
- `src/backend/ir/tacky.py` - IR AST definitions
- `src/backend/ir/tacky_emiter.py` - IR emission from AST

---

## 2. TACKY IR Design

### 2.1 Design Principles

TACKY IR follows these principles:
1. **Three-Address Code**: Each instruction has at most 3 operands
2. **Flat Structure**: No nested expressions; complex expressions are broken down
3. **Explicit Control Flow**: Jumps and labels instead of structured statements
4. **Typed Operations**: Each operation knows its operand types
5. **SSA-like Temporaries**: New temporaries for intermediate results

### 2.2 IR Program Structure

```
Program
└── TopLevel*
    ├── Function(name, params, body: Instruction*)
    └── StaticVariable(name, type, init)
```

---

## 3. TACKY IR Instructions

### 3.1 Value Operations

| Instruction | Format | Description |
|-------------|--------|-------------|
| `Copy` | `dst = src` | Copy value |
| `Unary` | `dst = op src` | Unary operation |
| `Binary` | `dst = left op right` | Binary operation |
| `Load` | `dst = *src` | Load from pointer |
| `Store` | `*dst = src` | Store to pointer |
| `GetAddress` | `dst = &src` | Get address |

### 3.2 Control Flow Instructions

| Instruction | Format | Description |
|-------------|--------|-------------|
| `Jump` | `goto label` | Unconditional jump |
| `JumpIfZero` | `if src == 0 goto label` | Conditional jump |
| `JumpIfNotZero` | `if src != 0 goto label` | Conditional jump |
| `Label` | `label:` | Jump target |
| `Return` | `return src` | Return from function |

### 3.3 Function Instructions

| Instruction | Format | Description |
|-------------|--------|-------------|
| `FunCall` | `dst = call func(args...)` | Function call |

### 3.4 Type Conversion

| Instruction | Format | Description |
|-------------|--------|-------------|
| `SignExtend` | `dst = sext src` | Sign extend |
| `ZeroExtend` | `dst = zext src` | Zero extend |
| `Truncate` | `dst = trunc src` | Truncate |
| `IntToDouble` | `dst = itod src` | Int to double |
| `DoubleToInt` | `dst = dtoi src` | Double to int |

---

## 4. TACKY Operands

### 4.1 Operand Types

```python
class Val:
    """Base class for all operand values"""
    pass

class Constant(Val):
    """Literal constant"""
    value: int | float

class Var(Val):
    """Variable or temporary"""
    name: str

class Tmp(Val):
    """Compiler-generated temporary"""
    name: str  # e.g., "tmp.1", "tmp.2"
```

### 4.2 Temporary Generation

```python
tmp_counter = 0

def make_temporary():
    global tmp_counter
    tmp_counter += 1
    return Tmp(f"tmp.{tmp_counter}")
```

---

## 5. Translation Rules

### 5.1 Expression Translation

**Binary Expression: `a + b * c`**
```
tmp.1 = b * c
tmp.2 = a + tmp.1
result = tmp.2
```

**Unary Expression: `-x`**
```
tmp.1 = negate x
result = tmp.1
```

**Comparison: `a < b`**
```
tmp.1 = a < b    ; produces 0 or 1
result = tmp.1
```

**Short-Circuit AND: `a && b`**
```
    tmp.1 = a
    if tmp.1 == 0 goto false_label
    tmp.2 = b
    if tmp.2 == 0 goto false_label
    tmp.3 = 1
    goto end_label
false_label:
    tmp.3 = 0
end_label:
    result = tmp.3
```

**Short-Circuit OR: `a || b`**
```
    tmp.1 = a
    if tmp.1 != 0 goto true_label
    tmp.2 = b
    if tmp.2 != 0 goto true_label
    tmp.3 = 0
    goto end_label
true_label:
    tmp.3 = 1
end_label:
    result = tmp.3
```

**Ternary: `a ? b : c`**
```
    tmp.1 = a
    if tmp.1 == 0 goto else_label
    tmp.2 = b
    goto end_label
else_label:
    tmp.2 = c
end_label:
    result = tmp.2
```

### 5.2 Statement Translation

**If-Else Statement:**
```c
if (condition) {
    then_body;
} else {
    else_body;
}
```
Translates to:
```
    tmp.1 = condition
    if tmp.1 == 0 goto else_label
    ; then_body instructions
    goto end_label
else_label:
    ; else_body instructions
end_label:
```

**While Loop:**
```c
while (condition) {
    body;
}
```
Translates to:
```
continue_label:
    tmp.1 = condition
    if tmp.1 == 0 goto break_label
    ; body instructions
    goto continue_label
break_label:
```

**For Loop:**
```c
for (init; condition; post) {
    body;
}
```
Translates to:
```
    ; init instructions
start_label:
    tmp.1 = condition
    if tmp.1 == 0 goto break_label
    ; body instructions
continue_label:
    ; post instructions
    goto start_label
break_label:
```

### 5.3 Function Translation

**Function Call: `result = foo(a, b, c)`**
```
    tmp.1 = a
    tmp.2 = b
    tmp.3 = c
    tmp.4 = call foo(tmp.1, tmp.2, tmp.3)
    result = tmp.4
```

**Return Statement: `return expr;`**
```
    tmp.1 = expr
    return tmp.1
```

---

## 6. Complete Translation Example

### Source Code:
```c
int factorial(int n) {
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}
```

### TACKY IR Output:
```
function factorial(n):
    ; if (n <= 1)
    tmp.1 = n <= 1
    if tmp.1 == 0 goto else.1

    ; return 1
    return 1

else.1:
    ; n - 1
    tmp.2 = n - 1

    ; factorial(n - 1)
    tmp.3 = call factorial(tmp.2)

    ; n * factorial(n - 1)
    tmp.4 = n * tmp.3

    ; return result
    return tmp.4
```

### More Complex Example:
```c
int sum_array(int *arr, int size) {
    int total = 0;
    for (int i = 0; i < size; i = i + 1) {
        total = total + arr[i];
    }
    return total;
}
```

### TACKY IR Output:
```
function sum_array(arr, size):
    ; int total = 0
    total = 0

    ; int i = 0
    i = 0

for.start.1:
    ; i < size
    tmp.1 = i < size
    if tmp.1 == 0 goto for.break.1

    ; arr[i] - compute address
    tmp.2 = i * 4           ; sizeof(int) = 4
    tmp.3 = arr + tmp.2     ; pointer arithmetic
    tmp.4 = *tmp.3          ; load arr[i]

    ; total = total + arr[i]
    tmp.5 = total + tmp.4
    total = tmp.5

for.continue.1:
    ; i = i + 1
    tmp.6 = i + 1
    i = tmp.6
    goto for.start.1

for.break.1:
    ; return total
    return total
```

---

## 7. IR Data Structures

### 7.1 Function Representation

```python
class TackyFunction:
    name: str
    params: List[str]
    body: List[Instruction]
    local_vars: Dict[str, Type]
```

### 7.2 Instruction Classes

```python
class Instruction:
    pass

class Copy(Instruction):
    src: Val
    dst: Val

class Binary(Instruction):
    op: BinaryOp
    left: Val
    right: Val
    dst: Val

class Unary(Instruction):
    op: UnaryOp
    src: Val
    dst: Val

class Jump(Instruction):
    target: str

class JumpIfZero(Instruction):
    condition: Val
    target: str

class Label(Instruction):
    name: str

class Return(Instruction):
    val: Val

class FunCall(Instruction):
    name: str
    args: List[Val]
    dst: Val
```

---

## 8. Running IR Generation

```bash
# Generate TACKY IR
python pcc --tacky examples/factorial.c

# Example output:
Tacky IR:
Function(name='factorial', params=['n'], body=[
    Binary(op=LE, left=Var('n'), right=Const(1), dst=Tmp('tmp.1')),
    JumpIfZero(condition=Tmp('tmp.1'), target='else.1'),
    Return(val=Const(1)),
    Label(name='else.1'),
    Binary(op=SUB, left=Var('n'), right=Const(1), dst=Tmp('tmp.2')),
    FunCall(name='factorial', args=[Tmp('tmp.2')], dst=Tmp('tmp.3')),
    Binary(op=MUL, left=Var('n'), right=Tmp('tmp.3'), dst=Tmp('tmp.4')),
    Return(val=Tmp('tmp.4'))
])
```

---

## 9. IR Properties

| Property | Description |
|----------|-------------|
| **Machine Independence** | No register references, no specific instruction set |
| **Type Preservation** | Operations maintain type information |
| **Explicit Addressing** | All memory accesses made explicit |
| **Linear Representation** | Flat sequence of instructions |
| **SSA-like** | Temporaries typically assigned once |

---

*This document describes the intermediate code generation phase of the Mini-C compiler.*
