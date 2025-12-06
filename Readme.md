# Mini-C Compiler (PCC)

## CS4031 - Compiler Construction | Fall 2025

A fully-featured **Mini-C compiler** for the x86-64 architecture, written entirely in Python. This project demonstrates all **six phases of compilation** as required for the CS4031 semester project.

---

## Project Overview

**Mini-C** is a domain-specific language designed for numerical computation and pattern generation. It is a carefully defined subset of C that supports:

- Mathematical computations (factorial, Fibonacci, GCD, prime checking)
- Array and pointer operations
- Structured data processing
- Control flow constructs (loops, conditionals, functions)

---

## Six Compilation Phases

| Phase | Description | Documentation |
|-------|-------------|---------------|
| 1. **Lexical Analysis** | Tokenization using handwritten lexer | [`docs/02_Lexical_Analysis.md`](docs/02_Lexical_Analysis.md) |
| 2. **Syntax Analysis** | Recursive-descent parser → AST | [`docs/03_Syntax_Analysis.md`](docs/03_Syntax_Analysis.md) |
| 3. **Semantic Analysis** | Type checking, symbol tables | [`docs/04_Semantic_Analysis.md`](docs/04_Semantic_Analysis.md) |
| 4. **Intermediate Code** | TACKY IR generation | [`docs/05_Intermediate_Code.md`](docs/05_Intermediate_Code.md) |
| 5. **Optimization** | Constant folding, dead store elimination | [`docs/06_Optimization.md`](docs/06_Optimization.md) |
| 6. **Code Generation** | x86-64 assembly output | [`docs/07_Code_Generation.md`](docs/07_Code_Generation.md) |

---

## Quick Start

### Requirements
- Python 3.12+
- GCC (for preprocessing, assembling, linking)

### Basic Usage

```bash
# View tokens (lexical analysis)
python pcc --lex test_cases/01_factorial.c

# View AST (syntax analysis)
python pcc --parse test_cases/01_factorial.c

# View symbol table (semantic analysis)
python pcc --validate test_cases/01_factorial.c

# View intermediate representation
python pcc --tacky test_cases/01_factorial.c

# Generate assembly
python pcc -S test_cases/01_factorial.c

# Full compilation
python pcc run test_cases/01_factorial.c -o factorial
./factorial
echo $?  # Output: 120
```

### Interactive Mode (CLI)

```bash
# Start interactive REPL
python pcc -i

# In interactive mode:
>>> int main(void) { return 42; }

# Press Enter on blank line to compile and run
```

### Graphical User Interface (GUI)

```bash
# Launch the GUI
python gui.py
```

The GUI provides:
- **Syntax Highlighting** - VS Code-style coloring for keywords, types, comments
- **Compilation Phase Buttons** - View output of each phase
- **8 Sample Programs** - factorial, fibonacci, GCD, power, prime, loops, etc.
- **Compiler Statistics** - Token count, symbol count, IR instructions, ASM lines
- **Export Functionality** - Export tokens, AST, symbols, IR, or assembly to files
- **Export All** - Export all compilation outputs to a single ZIP file

---

## Project Structure

```
Mini-C-Compiler/
├── pcc                     # Main compiler entry point
├── gui.py                  # Graphical user interface
├── src/
│   ├── frontend/
│   │   ├── lexer/          # Tokenizer
│   │   └── parser/         # Recursive-descent parser
│   └── backend/
│       ├── typechecker/    # Semantic analysis
│       ├── ir/             # TACKY IR generation
│       └── codegen/        # x86-64 code generation
├── docs/                   # Documentation for each phase
│   ├── 01_Language_Specification.md
│   ├── 02_Lexical_Analysis.md
│   ├── 03_Syntax_Analysis.md
│   ├── 04_Semantic_Analysis.md
│   ├── 05_Intermediate_Code.md
│   ├── 06_Optimization.md
│   ├── 07_Code_Generation.md
│   ├── 08_Reflection.md
│   └── handwritten/        # Handwritten artifacts (DFA, parse trees)
├── test_cases/             # 13 comprehensive test programs
│   ├── 01_factorial.c      # Recursion (returns 120)
│   ├── 02_fibonacci.c      # Double recursion (returns 55)
│   ├── 03_array_sum.c      # Arrays, pointers (returns 15)
│   ├── 04_gcd.c            # GCD algorithm (returns 6)
│   ├── 05_power.c          # Exponentiation (returns 32)
│   ├── 06_nested_loops.c   # Nested for loops (returns 36)
│   ├── 07_while_loop.c     # While loop (returns 55)
│   ├── 08_do_while.c       # Do-while loop (returns 10)
│   ├── 09_logical_ops.c    # AND, OR, NOT (returns 1)
│   ├── 10_ternary.c        # Ternary operator (returns 20)
│   ├── 11_multiple_funcs.c # Multiple functions (returns 25)
│   ├── 12_break_continue.c # Loop control (returns 12)
│   └── 13_prime_check.c    # Prime checking (returns 1)
└── examples/               # Additional examples
```

---

## Supported Mini-C Features

### Types
- `int`, `long`, `unsigned`, `signed`
- `char`, `double`, `void`
- Pointers (`int *`)
- Arrays (`int arr[10]`)
- Structs (`struct Point { int x; int y; }`)

### Control Flow
- `if` / `else`
- `while`, `do-while`, `for`
- `break`, `continue`
- `return`
- Ternary operator (`?:`)

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Logical: `&&`, `||`, `!`
- Assignment: `=`
- Pointer: `*`, `&`, `->`

---

## Test Cases

| # | Test | Description | Expected Return |
|---|------|-------------|-----------------|
| 1 | `01_factorial.c` | Recursive factorial (5!) | 120 |
| 2 | `02_fibonacci.c` | Fibonacci sequence (F(10)) | 55 |
| 3 | `03_array_sum.c` | Array sum with pointers | 15 |
| 4 | `04_gcd.c` | Greatest Common Divisor | 6 |
| 5 | `05_power.c` | Power function (2^5) | 32 |
| 6 | `06_nested_loops.c` | Nested for loops | 36 |
| 7 | `07_while_loop.c` | While loop accumulator | 55 |
| 8 | `08_do_while.c` | Do-while loop | 10 |
| 9 | `09_logical_ops.c` | Logical operators | 1 |
| 10 | `10_ternary.c` | Ternary operator | 20 |
| 11 | `11_multiple_funcs.c` | Multiple functions | 25 |
| 12 | `12_break_continue.c` | Break and continue | 12 |
| 13 | `13_prime_check.c` | Prime number check | 1 |

Run all tests:
```bash
# Windows
python pcc run test_cases/01_factorial.c -o test1 && test1 && echo %errorlevel%

# Linux/Mac
python pcc run test_cases/01_factorial.c -o test1 && ./test1; echo $?
```

---

## GUI Features

### Syntax Highlighting
The code editor features VS Code-style syntax highlighting:
- **Keywords** (blue): `if`, `else`, `while`, `for`, `return`
- **Types** (teal): `int`, `void`, `char`, `double`
- **Numbers** (light green): `123`, `3.14`
- **Strings** (orange): `"hello"`
- **Comments** (green): `// comment`, `/* block */`
- **Functions** (yellow): `main()`, `factorial()`

### Compiler Statistics
Real-time display of:
- Token count
- Symbol count
- IR instruction count
- Assembly line count

### Export Options
- Export Tokens (.txt)
- Export AST (.txt)
- Export Symbol Table (.txt)
- Export IR (.txt)
- Export Assembly (.s)
- Export All (.zip) - All outputs in one archive

---

## Documentation

### Language Specification
- [`docs/01_Language_Specification.md`](docs/01_Language_Specification.md) - BNF/EBNF grammar, lexical rules, semantic rules

### Phase Documentation
Each compilation phase has detailed documentation with examples and implementation details.

### Handwritten Artifacts
Place scanned handwritten documents in `docs/handwritten/`:
- DFA/Transition table
- Parse tree derivations (at least 2)
- Symbol table with scope example

See [`docs/handwritten/INSTRUCTIONS.md`](docs/handwritten/INSTRUCTIONS.md) for guidelines.

---

## Compilation Stages

| Flag | Stage | Output |
|------|-------|--------|
| `--lex` | Lexical Analysis | Token stream |
| `--parse` | Syntax Analysis | AST |
| `--validate` | Semantic Analysis | Symbol table |
| `--tacky` | IR Generation | TACKY IR |
| `--codegen` | Code Generation | Assembly AST |
| `-S` | Assembly | `.s` files |
| `-c` | Object Files | `.o` files |
| `run` | Full Compile | Executable |
| `-i` | Interactive | REPL mode |

---

## Credits

- Inspired by *Writing a C Compiler* by Nora Sandler
- System V x86-64 ABI documentation
- CS4031 Compiler Construction course

---

## Group Members

| Name | Contribution |
|------|--------------|
| [Member 1] | Lexical Analysis, Token Design |
| [Member 2] | Syntax Analysis, Parser Implementation |
| [Member 3] | Semantic Analysis, Type Checking |
| [Member 4] | IR Generation, TACKY Design |
| [Member 5] | Optimization Passes |
| [Member 6] | Code Generation, Testing, GUI |

---

## License

Educational and non-commercial use only.
