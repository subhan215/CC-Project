# Syntax Analysis Documentation

## CS4031 - Compiler Construction | Fall 2025

---

## 1. Overview

The parser (syntax analyzer) is the second phase of the Mini-C compiler. It takes a stream of tokens from the lexer and constructs an **Abstract Syntax Tree (AST)** that represents the hierarchical structure of the program.

**Location:** `src/frontend/parser/parser.py`
**Parsing Technique:** Recursive Descent Parser with Precedence Climbing for expressions

---

## 2. Grammar Summary

### 2.1 Top-Level Productions

```
Program        → Declaration*
Declaration    → FunctionDecl | VariableDecl | StructDecl
FunctionDecl   → TypeSpec Identifier '(' ParamList ')' (Block | ';')
VariableDecl   → TypeSpec Declarator ['=' Initializer] ';'
StructDecl     → 'struct' Identifier '{' MemberDecl* '}' ';'
```

### 2.2 Statement Productions

```
Statement      → CompoundStmt | ExprStmt | SelectionStmt | IterationStmt | JumpStmt
CompoundStmt   → '{' BlockItem* '}'
BlockItem      → Declaration | Statement
ExprStmt       → [Expression] ';'
SelectionStmt  → 'if' '(' Expression ')' Statement ['else' Statement]
IterationStmt  → WhileStmt | DoWhileStmt | ForStmt
WhileStmt      → 'while' '(' Expression ')' Statement
DoWhileStmt    → 'do' Statement 'while' '(' Expression ')' ';'
ForStmt        → 'for' '(' ForInit [Expression] ';' [Expression] ')' Statement
JumpStmt       → 'return' [Expression] ';' | 'break' ';' | 'continue' ';'
```

### 2.3 Expression Productions

```
Expression     → AssignmentExpr
AssignmentExpr → ConditionalExpr | UnaryExpr '=' AssignmentExpr
ConditionalExpr→ LogicalOrExpr ['?' Expression ':' ConditionalExpr]
LogicalOrExpr  → LogicalAndExpr ('||' LogicalAndExpr)*
LogicalAndExpr → EqualityExpr ('&&' EqualityExpr)*
EqualityExpr   → RelationalExpr (('==' | '!=') RelationalExpr)*
RelationalExpr → AdditiveExpr (('<' | '>' | '<=' | '>=') AdditiveExpr)*
AdditiveExpr   → MultExpr (('+' | '-') MultExpr)*
MultExpr       → CastExpr (('*' | '/' | '%') CastExpr)*
CastExpr       → '(' TypeName ')' CastExpr | UnaryExpr
UnaryExpr      → PostfixExpr | UnaryOp CastExpr | 'sizeof' UnaryExpr
PostfixExpr    → PrimaryExpr (Subscript | FuncCall | MemberAccess)*
PrimaryExpr    → Identifier | Constant | StringLiteral | '(' Expression ')'
```

---

## 3. AST Node Types

### 3.1 Program and Declaration Nodes

| Node | Fields | Description |
|------|--------|-------------|
| `Program` | `function_definition: List[Declaration]` | Root of AST |
| `FunDecl` | `name, params, fun_type, body, storage_class` | Function declaration |
| `VarDecl` | `name, init, var_type, storage_class` | Variable declaration |
| `StructDecl` | `tag, members` | Struct type declaration |
| `Parameter` | `_type, name, declarator` | Function parameter |
| `Member` | `name, _type` | Struct member |

### 3.2 Statement Nodes

| Node | Fields | Description |
|------|--------|-------------|
| `Return` | `exp` | Return statement |
| `If` | `exp, then, _else` | If-else statement |
| `While` | `exp, body` | While loop |
| `DoWhile` | `body, exp` | Do-while loop |
| `For` | `init, condition, post, body` | For loop |
| `Compound` | `block` | Block statement |
| `Expression` | `exp` | Expression statement |
| `Break` | - | Break statement |
| `Continue` | - | Continue statement |
| `Block` | `block_items` | List of block items |

### 3.3 Expression Nodes

| Node | Fields | Description |
|------|--------|-------------|
| `Binary` | `operator, left, right` | Binary operation |
| `Unary` | `operator, expr` | Unary operation |
| `Constant` | `value` | Literal constant |
| `Var` | `identifier` | Variable reference |
| `Assignment` | `left, right` | Assignment |
| `Conditional` | `condition, exp2, exp3` | Ternary operator |
| `FunctionCall` | `identifier, args` | Function call |
| `Cast` | `target_type, exp` | Type cast |
| `Subscript` | `array, index` | Array subscript |
| `Dot` | `structure, member` | Member access |
| `Arrow` | `pointer, member` | Pointer member access |
| `AddOf` | `expr` | Address-of operator |
| `Dereference` | `expr` | Pointer dereference |
| `SizeOf` | `expr` | sizeof expression |
| `SizeOfT` | `_type` | sizeof type |
| `String` | `string` | String literal |

### 3.4 Type Nodes

| Node | Fields | Description |
|------|--------|-------------|
| `Int` | - | 32-bit signed integer |
| `Long` | - | 64-bit signed integer |
| `UInt` | - | 32-bit unsigned integer |
| `ULong` | - | 64-bit unsigned integer |
| `Char` | - | 8-bit character |
| `SChar` | - | Signed char |
| `UChar` | - | Unsigned char |
| `Double` | - | 64-bit float |
| `Void` | - | Void type |
| `Pointer` | `referenced` | Pointer type |
| `Array` | `element, size` | Array type |
| `Structure` | `tag` | Struct type |
| `FunType` | `param_count, params, base_type` | Function type |

---

## 4. Parse Tree Derivations

### 4.1 Example 1: Simple Return Statement

**Source Code:**
```c
int main(void) {
    return 42;
}
```

**Derivation:**
```
Program
└── FunctionDecl
    ├── type: Int
    ├── name: "main"
    ├── params: [void]
    └── body: Block
        └── Return
            └── Constant
                └── value: 42
```

**Parse Tree (Concrete):**
```
                    Program
                       │
                 FunctionDecl
                 /    |    \
              Int  "main"  Block
                     |       │
                  ParamList  Return
                     |         │
                   void     Constant
                               │
                              42
```

### 4.2 Example 2: If-Else Statement

**Source Code:**
```c
int max(int a, int b) {
    if (a > b)
        return a;
    else
        return b;
}
```

**Derivation:**
```
Program
└── FunctionDecl
    ├── type: Int
    ├── name: "max"
    ├── params: [(Int, "a"), (Int, "b")]
    └── body: Block
        └── If
            ├── condition: Binary(GT)
            │   ├── left: Var("a")
            │   └── right: Var("b")
            ├── then: Return
            │   └── Var("a")
            └── else: Return
                └── Var("b")
```

**Parse Tree (Concrete):**
```
                         Program
                            │
                      FunctionDecl
                     /    |    |    \
                  Int  "max" Params  Block
                            /   \      │
                         (a)   (b)    If
                                    /  |  \
                              Cond Then Else
                               │    │    │
                            Binary Ret  Ret
                            /  |  \  │    │
                          a   >   b  a    b
```

### 4.3 Example 3: For Loop with Array

**Source Code:**
```c
int sum(int arr[5]) {
    int total = 0;
    for (int i = 0; i < 5; i = i + 1) {
        total = total + arr[i];
    }
    return total;
}
```

**Derivation:**
```
Program
└── FunctionDecl
    ├── type: Int
    ├── name: "sum"
    ├── params: [(Array[5] of Int, "arr")]
    └── body: Block
        ├── VarDecl
        │   ├── name: "total"
        │   ├── type: Int
        │   └── init: Constant(0)
        ├── For
        │   ├── init: VarDecl(Int, "i", 0)
        │   ├── condition: Binary(LT)
        │   │   ├── left: Var("i")
        │   │   └── right: Constant(5)
        │   ├── post: Assignment
        │   │   ├── left: Var("i")
        │   │   └── right: Binary(ADD)
        │   │       ├── left: Var("i")
        │   │       └── right: Constant(1)
        │   └── body: Block
        │       └── ExprStmt
        │           └── Assignment
        │               ├── left: Var("total")
        │               └── right: Binary(ADD)
        │                   ├── left: Var("total")
        │                   └── right: Subscript
        │                       ├── array: Var("arr")
        │                       └── index: Var("i")
        └── Return
            └── Var("total")
```

---

## 5. Operator Precedence Parsing

The parser uses **precedence climbing** for expression parsing:

```python
def parse_exp(tokens, min_prec=0):
    lhs = parse_cast_expr(tokens)

    while True:
        op = tokens[0]
        binop_info = get_precedence(op)
        if not binop_info or binop_info['precedence'] < min_prec:
            break

        prec = binop_info['precedence']
        assoc = binop_info['associativity']

        # Determine next minimum precedence
        if assoc == 'LEFT':
            next_min_prec = prec + 1
        else:  # RIGHT associative
            next_min_prec = prec

        consume_token(op)
        rhs = parse_exp(tokens, next_min_prec)
        lhs = Binary(op, lhs, rhs)

    return lhs
```

### Precedence Table Used:

| Precedence | Operators | Associativity |
|------------|-----------|---------------|
| 50 | `*` `/` `%` | LEFT |
| 45 | `+` `-` | LEFT |
| 35 | `<` `>` `<=` `>=` | LEFT |
| 30 | `==` `!=` | LEFT |
| 10 | `&&` | LEFT |
| 5 | `\|\|` | LEFT |
| 3 | `?:` | RIGHT |
| 1 | `=` | RIGHT |

---

## 6. Error Recovery

The parser reports syntax errors with descriptive messages:

```python
def expect(expected, tokens):
    if not tokens:
        raise SyntaxError(f"Expected '{expected}', but reached end of input")
    token = tokens.pop(0)
    if token != expected:
        raise SyntaxError(f"Expected '{expected}', got '{token}'")
```

### Common Syntax Errors:

| Error | Example | Message |
|-------|---------|---------|
| Missing semicolon | `int x = 5` | "Expected ';', got ..." |
| Unmatched parenthesis | `if (x > 5` | "Expected ')', got ..." |
| Invalid declaration | `int 123abc;` | "Expected identifier, got '123abc'" |
| Missing brace | `int f() { return 1;` | "Expected '}', got end of input" |

---

## 7. Handwritten Artifact Reference

**Required:** At least 2 Parse Tree Derivations (hand-drawn scan/photo)

The handwritten parse trees should include:
1. Tree structure with nodes clearly labeled
2. Terminal symbols at leaf nodes
3. Non-terminal symbols at internal nodes
4. Clear parent-child relationships

*See: `docs/handwritten/parse_tree_1.jpg` and `docs/handwritten/parse_tree_2.jpg`*

---

## 8. Running the Parser

```bash
# Parse a file and display the AST
python pcc --parse examples/factorial.c

# Example output:
Parsed AST:
Program(function_definition=[
  FunDecl(name=Identifier('factorial'),
          params=[Parameter(type=Int, name='n')],
          fun_type=FunType(...),
          body=Block([...]),
          storage_class=Null)
])
```

---

*This document describes the syntax analysis phase of the Mini-C compiler.*
