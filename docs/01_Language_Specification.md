# Mini-C Language Specification

## CS4031 - Compiler Construction | Fall 2025

**Project:** Mini-C Compiler - A Domain-Specific Language for Numerical Computation
**Group Members:** [Add your names here]
**Date:** [Add date]

---

## 1. Language Overview

**Mini-C** is a statically-typed, imperative programming language designed for **numerical computation and pattern generation**. It is a carefully designed subset of C, optimized for:

- Mathematical computations (factorial, Fibonacci, arithmetic sequences)
- Array and matrix operations
- Pointer-based data manipulation
- Structured data processing

The language compiles to x86-64 assembly and produces native executables.

---

## 2. Lexical Specification

### 2.1 Token Categories

| Token Type | Examples | Regex Pattern |
|------------|----------|---------------|
| Keywords | `int`, `return`, `if`, `while`, `for` | Reserved words |
| Identifiers | `sum`, `factorial`, `_count` | `[a-zA-Z_][a-zA-Z0-9_]*` |
| Integer Constants | `42`, `100L`, `255U` | `[0-9]+[lLuU]?` |
| Float Constants | `3.14`, `2.5e-3` | `[0-9]*\.[0-9]+([eE][+-]?[0-9]+)?` |
| Character Constants | `'a'`, `'\n'`, `'\x41'` | `'([^'\\]\|\\[abfnrtv0\\'"?])'` |
| String Literals | `"hello"`, `"line\n"` | `"([^"\\]\|\\[abfnrtv\\"])*"` |
| Operators | `+`, `-`, `*`, `/`, `==`, `&&` | See Section 2.3 |
| Delimiters | `(`, `)`, `{`, `}`, `;` | Single characters |

### 2.2 Keywords (Reserved Words)

```
int      long     unsigned   signed    char     double   void
struct   static   extern     return    if       else     while
do       for      break      continue  sizeof
```

### 2.3 Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+` `-` `*` `/` `%` |
| Relational | `<` `>` `<=` `>=` `==` `!=` |
| Logical | `&&` `\|\|` `!` |
| Bitwise | `~` `&` |
| Assignment | `=` |
| Pointer | `*` (dereference) `&` (address-of) |
| Member Access | `.` `->` |
| Other | `?:` (ternary) `sizeof` |

### 2.4 Comments and Whitespace

- Single-line comments: `// comment`
- Multi-line comments: `/* comment */`
- Whitespace: spaces, tabs, newlines (ignored except as token separators)

---

## 3. Syntax Specification (BNF/EBNF Grammar)

### 3.1 Program Structure

```ebnf
<program> ::= { <declaration> }

<declaration> ::= <variable-declaration>
               | <function-declaration>
               | <struct-declaration>
```

### 3.2 Declarations

```ebnf
<variable-declaration> ::= <type-specifier> <declarator> [ "=" <initializer> ] ";"

<function-declaration> ::= <type-specifier> <identifier> "(" <parameter-list> ")" <compound-statement>
                        | <type-specifier> <identifier> "(" <parameter-list> ")" ";"

<struct-declaration> ::= "struct" <identifier> "{" { <member-declaration> } "}" ";"

<member-declaration> ::= <type-specifier> <declarator> ";"

<parameter-list> ::= <parameter> { "," <parameter> }
                  | "void"
                  | <empty>

<parameter> ::= <type-specifier> <declarator>
```

### 3.3 Type Specifiers

```ebnf
<type-specifier> ::= <primitive-type> | <struct-type>

<primitive-type> ::= "int"
                  | "long"
                  | "unsigned" [ "int" | "long" ]
                  | "signed" [ "int" | "long" ]
                  | "char"
                  | "unsigned" "char"
                  | "signed" "char"
                  | "double"
                  | "void"

<struct-type> ::= "struct" <identifier>

<storage-class> ::= "static" | "extern"
```

### 3.4 Declarators

```ebnf
<declarator> ::= "*" <declarator>
              | <direct-declarator>

<direct-declarator> ::= <identifier>
                     | "(" <declarator> ")"
                     | <direct-declarator> "[" <constant> "]"
                     | <direct-declarator> "(" <parameter-list> ")"

<abstract-declarator> ::= "*" [ <abstract-declarator> ]
                       | <direct-abstract-declarator>

<direct-abstract-declarator> ::= "(" <abstract-declarator> ")"
                               | [ <direct-abstract-declarator> ] "[" <constant> "]"
```

### 3.5 Statements

```ebnf
<statement> ::= <compound-statement>
             | <expression-statement>
             | <selection-statement>
             | <iteration-statement>
             | <jump-statement>

<compound-statement> ::= "{" { <block-item> } "}"

<block-item> ::= <declaration> | <statement>

<expression-statement> ::= [ <expression> ] ";"

<selection-statement> ::= "if" "(" <expression> ")" <statement> [ "else" <statement> ]

<iteration-statement> ::= "while" "(" <expression> ")" <statement>
                       | "do" <statement> "while" "(" <expression> ")" ";"
                       | "for" "(" <for-init> [ <expression> ] ";" [ <expression> ] ")" <statement>

<for-init> ::= <variable-declaration> | [ <expression> ] ";"

<jump-statement> ::= "return" [ <expression> ] ";"
                  | "break" ";"
                  | "continue" ";"
```

### 3.6 Expressions

```ebnf
<expression> ::= <assignment-expression>

<assignment-expression> ::= <conditional-expression>
                         | <unary-expression> "=" <assignment-expression>

<conditional-expression> ::= <logical-or-expression>
                          | <logical-or-expression> "?" <expression> ":" <conditional-expression>

<logical-or-expression> ::= <logical-and-expression> { "||" <logical-and-expression> }

<logical-and-expression> ::= <equality-expression> { "&&" <equality-expression> }

<equality-expression> ::= <relational-expression> { ( "==" | "!=" ) <relational-expression> }

<relational-expression> ::= <additive-expression> { ( "<" | ">" | "<=" | ">=" ) <additive-expression> }

<additive-expression> ::= <multiplicative-expression> { ( "+" | "-" ) <multiplicative-expression> }

<multiplicative-expression> ::= <cast-expression> { ( "*" | "/" | "%" ) <cast-expression> }

<cast-expression> ::= "(" <type-name> ")" <cast-expression>
                   | <unary-expression>

<unary-expression> ::= <postfix-expression>
                    | <unary-operator> <cast-expression>
                    | "sizeof" <unary-expression>
                    | "sizeof" "(" <type-name> ")"

<unary-operator> ::= "-" | "~" | "!" | "*" | "&"

<postfix-expression> ::= <primary-expression>
                      | <postfix-expression> "[" <expression> "]"
                      | <postfix-expression> "(" [ <argument-list> ] ")"
                      | <postfix-expression> "." <identifier>
                      | <postfix-expression> "->" <identifier>

<primary-expression> ::= <identifier>
                      | <constant>
                      | <string-literal>
                      | "(" <expression> ")"

<argument-list> ::= <assignment-expression> { "," <assignment-expression> }
```

### 3.7 Constants

```ebnf
<constant> ::= <integer-constant>
            | <floating-constant>
            | <character-constant>

<integer-constant> ::= <decimal-constant> [ <integer-suffix> ]

<decimal-constant> ::= <nonzero-digit> { <digit> }
                    | "0"

<integer-suffix> ::= "u" | "U" | "l" | "L" | "ul" | "UL" | "lu" | "LU"

<floating-constant> ::= <fractional-constant> [ <exponent-part> ]
                     | <digit-sequence> <exponent-part>

<fractional-constant> ::= [ <digit-sequence> ] "." <digit-sequence>
                       | <digit-sequence> "."

<exponent-part> ::= ( "e" | "E" ) [ "+" | "-" ] <digit-sequence>

<character-constant> ::= "'" <c-char> "'"

<c-char> ::= <any-char-except-quote-backslash-newline>
          | <escape-sequence>

<escape-sequence> ::= "\\" ( "a" | "b" | "f" | "n" | "r" | "t" | "v" | "\\" | "'" | "\"" | "0" )
                   | "\\x" <hex-digit> <hex-digit>
```

---

## 4. Semantic Rules

### 4.1 Type System

Mini-C uses a static type system with the following types:

| Type | Size (bytes) | Range/Description |
|------|--------------|-------------------|
| `char` | 1 | -128 to 127 |
| `unsigned char` | 1 | 0 to 255 |
| `int` | 4 | -2^31 to 2^31-1 |
| `unsigned int` | 4 | 0 to 2^32-1 |
| `long` | 8 | -2^63 to 2^63-1 |
| `unsigned long` | 8 | 0 to 2^64-1 |
| `double` | 8 | IEEE 754 double precision |
| `void` | - | No value |
| `pointer` | 8 | Memory address |
| `array[N]` | N * element_size | Contiguous elements |
| `struct` | Sum of members | Composite type |

### 4.2 Type Compatibility Rules

1. **Integer Promotions**: `char` and `short` are promoted to `int` in expressions
2. **Usual Arithmetic Conversions**: Operands are converted to a common type
3. **Pointer Arithmetic**: Adding integer to pointer scales by element size
4. **Array Decay**: Arrays decay to pointers in most contexts

### 4.3 Scope Rules

1. **Block Scope**: Variables declared in `{ }` are visible only within that block
2. **File Scope**: Variables/functions declared outside functions are globally visible
3. **Function Scope**: Parameters are visible throughout the function body
4. **Shadowing**: Inner scope declarations shadow outer scope names

### 4.4 Storage Classes

| Storage Class | Meaning |
|---------------|---------|
| `static` (local) | Persists across function calls |
| `static` (global) | Internal linkage (file-private) |
| `extern` | External linkage (defined elsewhere) |

---

## 5. Example Programs

### 5.1 Factorial Computation

**Input:**
```c
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main(void) {
    int result = factorial(5);
    return result;
}
```

**Expected Output:** Program returns `120`

### 5.2 Fibonacci Sequence

**Input:**
```c
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main(void) {
    return fibonacci(10);
}
```

**Expected Output:** Program returns `55`

### 5.3 Array Sum with Pointers

**Input:**
```c
int sum_array(int *arr, int size) {
    int total = 0;
    for (int i = 0; i < size; i = i + 1) {
        total = total + arr[i];
    }
    return total;
}

int main(void) {
    int numbers[5] = {1, 2, 3, 4, 5};
    return sum_array(numbers, 5);
}
```

**Expected Output:** Program returns `15`

---

## 6. Operator Precedence Table

| Precedence | Operator | Associativity |
|------------|----------|---------------|
| 1 (highest) | `()` `[]` `.` `->` | Left-to-right |
| 2 | `!` `~` `-` `*` `&` `sizeof` | Right-to-left |
| 3 | `*` `/` `%` | Left-to-right |
| 4 | `+` `-` | Left-to-right |
| 5 | `<` `<=` `>` `>=` | Left-to-right |
| 6 | `==` `!=` | Left-to-right |
| 7 | `&&` | Left-to-right |
| 8 | `\|\|` | Left-to-right |
| 9 | `?:` | Right-to-left |
| 10 (lowest) | `=` | Right-to-left |

---

## 7. Error Handling

The Mini-C compiler reports errors at each compilation phase:

1. **Lexical Errors**: Invalid tokens, unterminated strings
2. **Syntax Errors**: Grammar violations, missing semicolons
3. **Semantic Errors**: Type mismatches, undeclared variables, scope violations
4. **Code Generation Errors**: Invalid operations for target architecture

---

*This specification defines Mini-C as implemented by the PCC compiler.*
