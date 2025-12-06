# Semantic Analysis Documentation

## CS4031 - Compiler Construction | Fall 2025

---

## 1. Overview

Semantic analysis is the third phase of the Mini-C compiler. It performs:
1. **Variable Resolution** - Binding identifiers to their declarations
2. **Type Checking** - Ensuring type compatibility in expressions
3. **Symbol Table Construction** - Managing scopes and declarations

**Location:**
- `src/backend/typechecker/variable_resolution.py`
- `src/backend/typechecker/typechecker.py`
- `src/backend/typechecker/type_classes.py`

---

## 2. Symbol Table Structure

### 2.1 Symbol Table Entry

Each symbol in the table contains:

```python
class SymbolEntry:
    name: str           # Identifier name
    type: Type          # Data type (Int, Pointer, Array, etc.)
    storage: Storage    # Storage class (Local, Static, Extern)
    scope_level: int    # Nesting depth
    offset: int         # Stack offset (for locals)
    is_defined: bool    # Whether fully defined
```

### 2.2 Storage Classes

| Storage Class | Description | Example |
|---------------|-------------|---------|
| `Local` | Stack-allocated local variable | `int x = 5;` |
| `Static` | Persistent across calls | `static int count = 0;` |
| `Extern` | Defined externally | `extern int global;` |
| `Global` | File-scope variable | Top-level `int g;` |

### 2.3 Symbol Table Operations

| Operation | Description |
|-----------|-------------|
| `insert(name, entry)` | Add new symbol to current scope |
| `lookup(name)` | Search for symbol in all scopes |
| `lookup_current(name)` | Search only in current scope |
| `enter_scope()` | Create new nested scope |
| `exit_scope()` | Remove current scope |

---

## 3. Type System

### 3.1 Type Hierarchy

```
Type
├── Void
├── Arithmetic Types
│   ├── Integer Types
│   │   ├── Char, SChar, UChar
│   │   ├── Int, UInt
│   │   └── Long, ULong
│   └── Floating Types
│       └── Double
├── Derived Types
│   ├── Pointer(referenced: Type)
│   ├── Array(element: Type, size: int)
│   └── Structure(tag: str)
└── Function Types
    └── FunType(params: List[Type], return_type: Type)
```

### 3.2 Type Sizes and Alignment

| Type | Size (bytes) | Alignment |
|------|--------------|-----------|
| `char` | 1 | 1 |
| `int` | 4 | 4 |
| `long` | 8 | 8 |
| `double` | 8 | 8 |
| `pointer` | 8 | 8 |
| `array[N]` | N * elem_size | elem_align |
| `struct` | sum of members | max member align |

### 3.3 Type Compatibility Rules

```python
def types_compatible(t1, t2):
    # Same type
    if t1 == t2:
        return True

    # Integer types are compatible with each other
    if is_integer(t1) and is_integer(t2):
        return True

    # Pointer to void is compatible with any pointer
    if is_pointer(t1) and is_pointer(t2):
        if is_void_ptr(t1) or is_void_ptr(t2):
            return True
        return types_compatible(t1.referenced, t2.referenced)

    # Array decays to pointer
    if is_array(t1) and is_pointer(t2):
        return types_compatible(Pointer(t1.element), t2)

    return False
```

---

## 4. Semantic Rules

### 4.1 Declaration Rules

| Rule | Description | Example Violation |
|------|-------------|-------------------|
| D1 | Variables must be declared before use | `x = 5;` (x not declared) |
| D2 | No duplicate declarations in same scope | `int x; int x;` |
| D3 | Function parameters must have unique names | `int f(int a, int a)` |
| D4 | Arrays must have positive constant size | `int arr[-1];` |
| D5 | Struct members must have unique names | `struct { int x; int x; }` |

### 4.2 Type Checking Rules

| Rule | Description | Example Violation |
|------|-------------|-------------------|
| T1 | Arithmetic operators require numeric operands | `"hello" + 5` |
| T2 | Comparison operators require compatible types | `5 < "str"` |
| T3 | Logical operators require scalar types | `struct_var && 1` |
| T4 | Assignment requires compatible types | `int *p = 5;` |
| T5 | Function call arguments must match parameters | `f(1, 2)` when `f(int)` |
| T6 | Return type must match function declaration | `int f() { return "x"; }` |
| T7 | Array subscript must be integer | `arr[3.14]` |
| T8 | Dereference requires pointer type | `*42` |
| T9 | Member access requires struct type | `(5).member` |

### 4.3 Scope Rules

| Rule | Description |
|------|-------------|
| S1 | Inner scope can shadow outer scope |
| S2 | Variables are visible from point of declaration |
| S3 | Function scope includes parameters |
| S4 | Block scope ends at closing brace |

---

## 5. Integer Promotions and Conversions

### 5.1 Integer Promotion Rules

```python
def promote_integer(type):
    """Promote small integers to int"""
    if type in [Char, SChar, UChar]:
        return Int
    return type
```

### 5.2 Usual Arithmetic Conversions

```python
def common_type(t1, t2):
    """Find common type for binary operation"""
    # Both same type
    if t1 == t2:
        return t1

    # If either is double, result is double
    if t1 == Double or t2 == Double:
        return Double

    # If either is unsigned long, result is unsigned long
    if t1 == ULong or t2 == ULong:
        return ULong

    # If either is long, result is long
    if t1 == Long or t2 == Long:
        return Long

    # If either is unsigned int, result is unsigned int
    if t1 == UInt or t2 == UInt:
        return UInt

    # Default to int
    return Int
```

---

## 6. Symbol Table Example

### Source Code:
```c
int global_var = 10;

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    int result = n * factorial(n - 1);
    return result;
}

int main(void) {
    int x = 5;
    int y = factorial(x);
    return y;
}
```

### Symbol Table State at Different Points:

**After parsing global declarations:**
```
┌─────────────────────────────────────────────────────────────────┐
│ SYMBOL TABLE - Scope Level 0 (Global)                           │
├──────────────┬──────────────────┬─────────┬──────────┬──────────┤
│ Name         │ Type             │ Storage │ Defined  │ Offset   │
├──────────────┼──────────────────┼─────────┼──────────┼──────────┤
│ global_var   │ Int              │ Global  │ Yes      │ -        │
│ factorial    │ FunType(Int→Int) │ Global  │ Yes      │ -        │
│ main         │ FunType(Void→Int)│ Global  │ Yes      │ -        │
└──────────────┴──────────────────┴─────────┴──────────┴──────────┘
```

**Inside factorial function (at `int result = ...`):**
```
┌─────────────────────────────────────────────────────────────────┐
│ SYMBOL TABLE - Scope Level 1 (Function: factorial)              │
├──────────────┬──────────────────┬─────────┬──────────┬──────────┤
│ Name         │ Type             │ Storage │ Defined  │ Offset   │
├──────────────┼──────────────────┼─────────┼──────────┼──────────┤
│ n            │ Int              │ Local   │ Yes      │ -8       │
│ result       │ Int              │ Local   │ Yes      │ -12      │
└──────────────┴──────────────────┴─────────┴──────────┴──────────┘
│ Parent Scope: Global (Level 0)                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Inside main function:**
```
┌─────────────────────────────────────────────────────────────────┐
│ SYMBOL TABLE - Scope Level 1 (Function: main)                   │
├──────────────┬──────────────────┬─────────┬──────────┬──────────┤
│ Name         │ Type             │ Storage │ Defined  │ Offset   │
├──────────────┼──────────────────┼─────────┼──────────┼──────────┤
│ x            │ Int              │ Local   │ Yes      │ -8       │
│ y            │ Int              │ Local   │ Yes      │ -12      │
└──────────────┴──────────────────┴─────────┴──────────┴──────────┘
│ Parent Scope: Global (Level 0)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Type Checking Examples

### Example 1: Valid Type Usage
```c
int arr[5] = {1, 2, 3, 4, 5};
int *ptr = arr;           // Array decays to pointer - OK
int val = ptr[2];         // Pointer subscript - OK
int sum = arr[0] + val;   // Int + Int - OK
```

### Example 2: Type Errors
```c
int x = "hello";          // ERROR: Cannot assign char* to int
double *dp = &x;          // ERROR: Cannot assign int* to double*
int y = arr;              // ERROR: Cannot assign array to int
x();                      // ERROR: x is not a function
```

### Example 3: Implicit Conversions
```c
int i = 10;
long l = i;               // OK: int promoted to long
double d = l;             // OK: long converted to double
char c = 'A';
int ascii = c;            // OK: char promoted to int (65)
```

---

## 8. Implementation Details

### 8.1 Variable Resolution Pass

```python
def resolve_variable(ast, symbols):
    """First pass: resolve variable names to declarations"""
    for decl in ast.declarations:
        if isinstance(decl, VarDecl):
            # Check for redeclaration
            if symbols.lookup_current(decl.name):
                raise SemanticError(f"Redeclaration of '{decl.name}'")
            # Add to symbol table
            symbols.insert(decl.name, create_entry(decl))

        elif isinstance(decl, FunDecl):
            # Enter function scope
            symbols.enter_scope()
            # Add parameters
            for param in decl.params:
                symbols.insert(param.name, create_entry(param))
            # Process body
            resolve_block(decl.body, symbols)
            symbols.exit_scope()
```

### 8.2 Type Checking Pass

```python
def typecheck_expression(expr, symbols):
    """Check types and annotate expression with result type"""
    if isinstance(expr, Binary):
        left_type = typecheck_expression(expr.left, symbols)
        right_type = typecheck_expression(expr.right, symbols)

        if expr.operator in [ADD, SUB, MUL, DIV]:
            if not (is_numeric(left_type) and is_numeric(right_type)):
                raise TypeError("Arithmetic requires numeric operands")
            return common_type(left_type, right_type)

        elif expr.operator in [LT, GT, LE, GE, EQ, NE]:
            if not types_compatible(left_type, right_type):
                raise TypeError("Comparison requires compatible types")
            return Int  # Comparisons return int

    elif isinstance(expr, Var):
        entry = symbols.lookup(expr.name)
        if not entry:
            raise SemanticError(f"Undefined variable '{expr.name}'")
        return entry.type

    # ... other cases
```

---

## 9. Handwritten Artifact Reference

**Required:** Sample Symbol Table with Scope Example (hand-drawn scan/photo)

The handwritten symbol table should include:
1. Table structure with columns (Name, Type, Storage, Scope, etc.)
2. Multiple scope levels shown
3. Example of variable shadowing
4. Clear indication of scope boundaries

*See: `docs/handwritten/symbol_table.jpg`*

---

## 10. Running Semantic Analysis

```bash
# Run semantic analysis and display symbol table
python pcc --validate examples/factorial.c

# Example output:
Validated AST:
Program(...)

Symbols after validation:
{
  'global_var': Entry(type=Int, storage=Global),
  'factorial': Entry(type=FunType(Int->Int), storage=Global),
  'main': Entry(type=FunType(Void->Int), storage=Global)
}

Type Table:
{
  'Point': StructType(members=[('x', Int), ('y', Int)])
}
```

---

*This document describes the semantic analysis phase of the Mini-C compiler.*
