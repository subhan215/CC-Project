# Lexical Analysis Documentation

## CS4031 - Compiler Construction | Fall 2025

---

## 1. Overview

The lexer (lexical analyzer) is the first phase of the Mini-C compiler. It converts the source code (a stream of characters) into a stream of **tokens** that are passed to the parser.

**Location:** `src/frontend/lexer/lexer.py`

---

## 2. Token Definitions

### 2.1 Token Categories

| Category | Token Name | Pattern (Regex) | Example |
|----------|------------|-----------------|---------|
| **Keywords** | | | |
| | `static` | `\bstatic\b` | `static` |
| | `extern` | `\bextern\b` | `extern` |
| | `long_keyword` | `\blong\b` | `long` |
| | `signed_keyword` | `\bsigned\b` | `signed` |
| | `unsigned_keyword` | `\bunsigned\b` | `unsigned` |
| | `struct_keyword` | `\bstruct\b` | `struct` |
| | `sizeof_keyword` | `\bsizeof\b` | `sizeof` |
| | `char` | `\bchar\b` | `char` |
| | `double_keyword` | `\bdouble\b` | `double` |
| | `int_keyword` | `int\b` | `int` |
| | `void_keyword` | `void\b` | `void` |
| | `return_keyword` | `return\b` | `return` |
| | `if_keyword` | `\bif\b` | `if` |
| | `else_keyword` | `\belse\b` | `else` |
| | `while` | `\bwhile\b` | `while` |
| | `do` | `\bdo\b` | `do` |
| | `for` | `\bfor\b` | `for` |
| | `break` | `\bbreak\b` | `break` |
| | `continue` | `\bcontinue\b` | `continue` |
| **Literals** | | | |
| | `Constant` | `[0-9]+` | `42`, `100` |
| | `unsigned_int_constant` | `[0-9]+[uU]` | `42U` |
| | `long_int_constant` | `[0-9]+[lL]` | `100L` |
| | `signed_long_constant` | `[0-9]+([lL][uU]\|[uU][lL])` | `100UL` |
| | `floating_point_constant` | `[0-9]*\.[0-9]+([eE][+-]?[0-9]+)?` | `3.14`, `2.5e-3` |
| | `char_constant` | `'...'` (with escapes) | `'a'`, `'\n'` |
| | `string_constant` | `"..."` (with escapes) | `"hello"` |
| **Operators** | | | |
| | `arrow` | `->` | `->` |
| | `dot` | `\.(?!\d)` | `.` |
| | `Complement` | `~` | `~` |
| | `Decrement` | `--` | `--` |
| | `Negation` | `-` | `-` |
| | `Multiplication` | `\*` | `*` |
| | `Addition` | `\+` | `+` |
| | `Division` | `/` | `/` |
| | `Remainder` | `%` | `%` |
| | `And` | `&&` | `&&` |
| | `Or` | `\|\|` | `\|\|` |
| | `Equal` | `==` | `==` |
| | `NotEqual` | `!=` | `!=` |
| | `LessOrEqual` | `<=` | `<=` |
| | `GreaterOrEqual` | `>=` | `>=` |
| | `LessThan` | `<` | `<` |
| | `GreaterThan` | `>` | `>` |
| | `Not` | `!` | `!` |
| | `Assignment` | `=` | `=` |
| | `Ampersand` | `&` | `&` |
| **Delimiters** | | | |
| | `Open_bracket` | `\[` | `[` |
| | `Close_bracket` | `\]` | `]` |
| | `Open_parenthesis` | `\(` | `(` |
| | `Close_parenthesis` | `\)` | `)` |
| | `Open_brace` | `{` | `{` |
| | `Close_brace` | `}` | `}` |
| | `Semicolon` | `;` | `;` |
| | `comma` | `,` | `,` |
| | `question_mark` | `?` | `?` |
| | `colon` | `:` | `:` |
| **Identifiers** | | | |
| | `Identifier` | `[a-zA-Z_]\w*\b` | `sum`, `_count` |

---

## 3. DFA (Deterministic Finite Automaton) Description

### 3.1 Main DFA States

```
State Diagram for Mini-C Lexer:

    START ──────────────────────────────────────────────────────────────────
      │
      ├──[a-zA-Z_]──> q1 (IDENTIFIER) ──[a-zA-Z0-9_]*──> q1 ──> ACCEPT_ID
      │
      ├──[0-9]──> q2 (INTEGER) ──[0-9]*──> q2 ──> ACCEPT_INT
      │                │
      │                ├──[.]──> q3 (FLOAT) ──[0-9]+──> q3 ──> ACCEPT_FLOAT
      │                │
      │                ├──[uU]──> ACCEPT_UINT
      │                │
      │                └──[lL]──> q4 ──[uU]?──> ACCEPT_LONG
      │
      ├──[']──> q5 (CHAR_START) ──[char/escape]──> q6 ──[']──> ACCEPT_CHAR
      │
      ├──["]──> q7 (STRING_START) ──[chars/escapes]*──> q7 ──["]──> ACCEPT_STRING
      │
      ├──[+]──> ACCEPT_PLUS
      ├──[-]──> q8 ──[-]──> ACCEPT_DECREMENT
      │         └──[>]──> ACCEPT_ARROW
      │         └──> ACCEPT_MINUS
      ├──[*]──> ACCEPT_MULT
      ├──[/]──> ACCEPT_DIV
      ├──[%]──> ACCEPT_MOD
      │
      ├──[<]──> q9 ──[=]──> ACCEPT_LE
      │         └──> ACCEPT_LT
      ├──[>]──> q10 ──[=]──> ACCEPT_GE
      │          └──> ACCEPT_GT
      ├──[=]──> q11 ──[=]──> ACCEPT_EQ
      │          └──> ACCEPT_ASSIGN
      ├──[!]──> q12 ──[=]──> ACCEPT_NE
      │          └──> ACCEPT_NOT
      │
      ├──[&]──> q13 ──[&]──> ACCEPT_AND
      │          └──> ACCEPT_AMPERSAND
      ├──[|]──> q14 ──[|]──> ACCEPT_OR
      │
      ├──[(]──> ACCEPT_LPAREN
      ├──[)]──> ACCEPT_RPAREN
      ├──[{]──> ACCEPT_LBRACE
      ├──[}]──> ACCEPT_RBRACE
      ├──[[]──> ACCEPT_LBRACKET
      ├──[]]──> ACCEPT_RBRACKET
      ├──[;]──> ACCEPT_SEMICOLON
      ├──[,]──> ACCEPT_COMMA
      ├──[.]──> ACCEPT_DOT
      ├──[?]──> ACCEPT_QUESTION
      ├──[:]──> ACCEPT_COLON
      ├──[~]──> ACCEPT_COMPLEMENT
      │
      └──[whitespace]──> START (skip)
```

### 3.2 Transition Table for Identifiers and Keywords

| Current State | Input | Next State | Action |
|---------------|-------|------------|--------|
| START | `[a-zA-Z_]` | q1 | Begin identifier |
| q1 | `[a-zA-Z0-9_]` | q1 | Continue identifier |
| q1 | other | ACCEPT | Check if keyword |

### 3.3 Transition Table for Numbers

| Current State | Input | Next State | Action |
|---------------|-------|------------|--------|
| START | `[0-9]` | q2 | Begin integer |
| q2 | `[0-9]` | q2 | Continue integer |
| q2 | `.` | q3 | Begin float |
| q2 | `[uU]` | ACCEPT_UINT | Unsigned int |
| q2 | `[lL]` | q4 | Long suffix |
| q3 | `[0-9]` | q3 | Continue float |
| q3 | `[eE]` | q5 | Begin exponent |
| q4 | `[uU]` | ACCEPT_ULONG | Unsigned long |
| q4 | other | ACCEPT_LONG | Long int |
| q5 | `[+-]?[0-9]+` | ACCEPT_FLOAT | Complete float |

### 3.4 Transition Table for Character Constants

| Current State | Input | Next State | Action |
|---------------|-------|------------|--------|
| START | `'` | CHAR_START | Begin char |
| CHAR_START | `[^'\\\n]` | CHAR_BODY | Regular char |
| CHAR_START | `\\` | ESCAPE | Escape sequence |
| ESCAPE | `[abfnrtv0\\'"]` | CHAR_BODY | Simple escape |
| ESCAPE | `x` | HEX_ESC | Hex escape |
| HEX_ESC | `[0-9a-fA-F]{2}` | CHAR_BODY | Hex value |
| CHAR_BODY | `'` | ACCEPT_CHAR | End char |

---

## 4. Lexer Implementation

### 4.1 Algorithm

```python
def lex(source_code):
    tokens = []
    position = 0

    while position < len(source_code):
        # Skip whitespace
        if is_whitespace(source_code[position]):
            position += 1
            continue

        # Try each pattern in priority order
        for token_type, pattern in patterns:
            match = regex_match(pattern, source_code, position)
            if match:
                tokens.append((token_type, match.group()))
                position = match.end()
                break
        else:
            raise LexicalError(f"Invalid character at position {position}")

    return tokens
```

### 4.2 Token Priority

Patterns are matched in the following priority order:
1. Keywords (matched before identifiers)
2. Multi-character operators (`<=`, `>=`, `==`, `!=`, `&&`, `||`, `->`)
3. Single-character operators
4. Literals (numbers, strings, characters)
5. Identifiers

---

## 5. Example Lexical Analysis

### Input:
```c
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
```

### Output Token Stream:
```
(int_keyword, 'int')
(Identifier, 'factorial')
(Open_parenthesis, '(')
(int_keyword, 'int')
(Identifier, 'n')
(Close_parenthesis, ')')
(Open_brace, '{')
(if_keyword, 'if')
(Open_parenthesis, '(')
(Identifier, 'n')
(LessOrEqual, '<=')
(Constant, '1')
(Close_parenthesis, ')')
(return_keyword, 'return')
(Constant, '1')
(Semicolon, ';')
(return_keyword, 'return')
(Identifier, 'n')
(Multiplication, '*')
(Identifier, 'factorial')
(Open_parenthesis, '(')
(Identifier, 'n')
(Negation, '-')
(Constant, '1')
(Close_parenthesis, ')')
(Semicolon, ';')
(Close_brace, '}')
```

---

## 6. Handwritten Artifact Reference

**Required:** DFA/Transition Table (hand-drawn scan/photo)

The handwritten DFA diagram should include:
1. State circles with labels (START, q1, q2, etc.)
2. Transition arrows with input labels
3. Accept states (double circles)
4. Clear indication of token types produced

*See: `docs/handwritten/DFA_diagram.jpg`*

---

## 7. Error Handling

| Error Type | Example | Error Message |
|------------|---------|---------------|
| Invalid character | `@` | "Unexpected character '@'" |
| Unterminated string | `"hello` | "Unterminated string literal" |
| Unterminated char | `'a` | "Unterminated character constant" |
| Invalid escape | `'\z'` | "Invalid escape sequence" |
| Number too large | `99999999999999999999` | "Integer constant too large" |

---

*This document describes the lexical analysis phase of the Mini-C compiler.*
