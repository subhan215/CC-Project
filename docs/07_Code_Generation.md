# Code Generation Documentation

## CS4031 - Compiler Construction | Fall 2025

---

## 1. Overview

Code generation is the final phase of the Mini-C compiler. It transforms TACKY IR into **x86-64 assembly** following the System V AMD64 ABI calling convention.

**Location:**
- `src/backend/codegen/assembly_ast.py` - Assembly AST definitions
- `src/backend/codegen/converter.py` - IR to Assembly conversion
- `src/backend/codegen/pseudoregister_replacer.py` - Register allocation
- `src/backend/codegen/instruction_fixer.py` - Instruction legalization
- `src/backend/codegen/code_emitter.py` - Assembly text output

---

## 2. Target Architecture: x86-64

### 2.1 Registers

| Register | Purpose | Callee-Saved |
|----------|---------|--------------|
| `%rax` | Return value, accumulator | No |
| `%rbx` | General purpose | Yes |
| `%rcx` | 4th argument | No |
| `%rdx` | 3rd argument | No |
| `%rsi` | 2nd argument | No |
| `%rdi` | 1st argument | No |
| `%rbp` | Base pointer | Yes |
| `%rsp` | Stack pointer | Yes |
| `%r8` | 5th argument | No |
| `%r9` | 6th argument | No |
| `%r10` | Temporary | No |
| `%r11` | Temporary | No |
| `%r12`-`%r15` | General purpose | Yes |

### 2.2 Register Variants by Size

| 64-bit | 32-bit | 16-bit | 8-bit |
|--------|--------|--------|-------|
| `%rax` | `%eax` | `%ax` | `%al` |
| `%rbx` | `%ebx` | `%bx` | `%bl` |
| `%rcx` | `%ecx` | `%cx` | `%cl` |
| `%rdx` | `%edx` | `%dx` | `%dl` |
| `%rdi` | `%edi` | `%di` | `%dil` |
| `%rsi` | `%esi` | `%si` | `%sil` |
| `%r8` | `%r8d` | `%r8w` | `%r8b` |

### 2.3 Floating-Point Registers (XMM)

| Register | Purpose |
|----------|---------|
| `%xmm0` | 1st float arg, float return |
| `%xmm1`-`%xmm7` | Float arguments 2-8 |
| `%xmm8`-`%xmm15` | Temporary |

---

## 3. System V AMD64 ABI Calling Convention

### 3.1 Argument Passing

**Integer/Pointer Arguments:**
- Arguments 1-6: `%rdi`, `%rsi`, `%rdx`, `%rcx`, `%r8`, `%r9`
- Arguments 7+: Pushed on stack (right to left)

**Floating-Point Arguments:**
- Arguments 1-8: `%xmm0` - `%xmm7`
- Arguments 9+: Pushed on stack

### 3.2 Return Values

| Type | Register |
|------|----------|
| Integer/Pointer | `%rax` |
| Floating-point | `%xmm0` |
| Struct (small) | `%rax`, `%rdx` |
| Struct (large) | Via pointer |

### 3.3 Stack Frame Layout

```
High Address
┌─────────────────────────────┐
│ Argument 8 (if needed)      │  +24(%rbp)
├─────────────────────────────┤
│ Argument 7 (if needed)      │  +16(%rbp)
├─────────────────────────────┤
│ Return Address              │  +8(%rbp)
├─────────────────────────────┤
│ Saved %rbp                  │  (%rbp)      ← Frame pointer
├─────────────────────────────┤
│ Local Variable 1            │  -8(%rbp)
├─────────────────────────────┤
│ Local Variable 2            │  -16(%rbp)
├─────────────────────────────┤
│ Saved Callee Registers      │
├─────────────────────────────┤
│ Temporary Storage           │
├─────────────────────────────┤
│ (Stack must be 16-aligned)  │  (%rsp)      ← Stack pointer
└─────────────────────────────┘
Low Address
```

---

## 4. Code Generation Pipeline

```
TACKY IR
    │
    ▼
┌─────────────────────────┐
│ 1. Instruction Selection│  IR → Assembly AST (with pseudo-registers)
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 2. Register Allocation  │  Map pseudo-registers to stack slots
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 3. Instruction Fixing   │  Handle x86-64 constraints
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 4. Code Emission        │  Generate AT&T assembly text
└─────────────────────────┘
    │
    ▼
Assembly File (.s)
```

---

## 5. Instruction Selection

### 5.1 TACKY to x86-64 Mapping

| TACKY Instruction | x86-64 Assembly |
|-------------------|-----------------|
| `dst = src` (Copy) | `movl src, dst` |
| `dst = -src` (Negate) | `movl src, dst; negl dst` |
| `dst = ~src` (Complement) | `movl src, dst; notl dst` |
| `dst = !src` (Not) | `cmpl $0, src; sete %al; movzbl %al, dst` |
| `dst = a + b` | `movl a, dst; addl b, dst` |
| `dst = a - b` | `movl a, dst; subl b, dst` |
| `dst = a * b` | `movl a, %eax; imull b; movl %eax, dst` |
| `dst = a / b` | `movl a, %eax; cdq; idivl b; movl %eax, dst` |
| `dst = a % b` | `movl a, %eax; cdq; idivl b; movl %edx, dst` |

### 5.2 Comparison and Conditional

| TACKY | x86-64 |
|-------|--------|
| `dst = a < b` | `cmpl b, a; setl %al; movzbl %al, dst` |
| `dst = a <= b` | `cmpl b, a; setle %al; movzbl %al, dst` |
| `dst = a > b` | `cmpl b, a; setg %al; movzbl %al, dst` |
| `dst = a >= b` | `cmpl b, a; setge %al; movzbl %al, dst` |
| `dst = a == b` | `cmpl b, a; sete %al; movzbl %al, dst` |
| `dst = a != b` | `cmpl b, a; setne %al; movzbl %al, dst` |

### 5.3 Control Flow

| TACKY | x86-64 |
|-------|--------|
| `goto label` | `jmp label` |
| `if x == 0 goto L` | `cmpl $0, x; je L` |
| `if x != 0 goto L` | `cmpl $0, x; jne L` |
| `label:` | `label:` |
| `return x` | `movl x, %eax; leave; ret` |

### 5.4 Function Calls

```
; call f(a, b, c)
movl a, %edi       ; 1st argument
movl b, %esi       ; 2nd argument
movl c, %edx       ; 3rd argument
call f
movl %eax, result  ; Get return value
```

---

## 6. Register Allocation

The Mini-C compiler uses a simple **stack-based allocation**:

### 6.1 Algorithm

```python
def allocate_registers(function):
    stack_offset = 0
    var_locations = {}

    for var in function.variables:
        size = get_size(var.type)
        alignment = get_alignment(var.type)

        # Align stack offset
        stack_offset = align_to(stack_offset, alignment)
        stack_offset += size

        var_locations[var] = StackSlot(-stack_offset)

    # Ensure 16-byte alignment
    function.stack_size = align_to(stack_offset, 16)

    return var_locations
```

### 6.2 Pseudo-Register Replacement

Before:
```asm
movl $5, tmp.1
addl tmp.2, tmp.1
movl tmp.1, result
```

After (pseudo-registers → stack slots):
```asm
movl $5, -8(%rbp)
movl -16(%rbp), %eax
addl %eax, -8(%rbp)
movl -8(%rbp), %eax
movl %eax, -24(%rbp)
```

---

## 7. Instruction Fixing

x86-64 has constraints that require instruction fixing:

### 7.1 Two-Address Form

Most x86 instructions modify one operand in place:
```asm
; Cannot do: addl mem1, mem2
; Must use register as intermediate:
movl mem1, %eax
addl %eax, mem2
```

### 7.2 Immediate Size Limits

```asm
; Cannot do: movq $0x123456789, %rax (large immediate)
; Must do:
movabsq $0x123456789, %rax
```

### 7.3 Division Requirements

```asm
; idiv divides %edx:%eax by operand
; Must set up %edx properly:
movl dividend, %eax
cdq                    ; Sign-extend %eax into %edx
idivl divisor
; Quotient in %eax, remainder in %edx
```

---

## 8. Complete Code Generation Example

### Source Code:
```c
int factorial(int n) {
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}
```

### Generated Assembly (AT&T Syntax):
```asm
    .globl factorial
    .text
factorial:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $16, %rsp           # Allocate stack space

    # Save parameter n
    movl    %edi, -4(%rbp)      # n at -4(%rbp)

    # if (n <= 1)
    cmpl    $1, -4(%rbp)
    jg      .L_else1            # Jump if n > 1

    # return 1
    movl    $1, %eax
    leave
    ret

.L_else1:
    # n - 1
    movl    -4(%rbp), %eax
    subl    $1, %eax

    # factorial(n - 1)
    movl    %eax, %edi          # Pass argument
    call    factorial
    movl    %eax, -8(%rbp)      # Save result

    # n * factorial(n - 1)
    movl    -4(%rbp), %eax
    imull   -8(%rbp), %eax

    # return
    leave
    ret
```

---

## 9. Assembly Directives

| Directive | Purpose |
|-----------|---------|
| `.globl name` | Export symbol |
| `.text` | Code section |
| `.data` | Initialized data section |
| `.bss` | Uninitialized data section |
| `.align n` | Align to n-byte boundary |
| `.long value` | 4-byte integer |
| `.quad value` | 8-byte integer |
| `.string "..."` | Null-terminated string |

---

## 10. Running Code Generation

```bash
# Generate assembly
python pcc -S examples/factorial.c

# Output: examples/factorial.s

# Full compilation (assemble + link)
python pcc run examples/factorial.c -o factorial

# Run the executable
./factorial
echo $?    # Print return value
```

---

## 11. Assembly Output Format

The compiler generates **AT&T syntax** assembly:

| AT&T | Intel | Note |
|------|-------|------|
| `movl $5, %eax` | `mov eax, 5` | Source, Destination order |
| `%eax` | `eax` | Register prefix |
| `$5` | `5` | Immediate prefix |
| `(%rax)` | `[rax]` | Memory reference |
| `8(%rbp)` | `[rbp+8]` | Displacement |
| `movl` | `mov dword` | Size suffix |

---

*This document describes the code generation phase of the Mini-C compiler.*
