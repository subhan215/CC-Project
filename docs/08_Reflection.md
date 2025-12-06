# Project Reflection

## CS4031 - Compiler Construction | Fall 2025

**Project:** Mini-C Compiler
**Group Members:** [Add your names here]
**Date:** [Add date]

---

## What We Learned

### 1. Compiler Architecture
Building this compiler gave us hands-on experience with the **six phases of compilation**:

- **Lexical Analysis**: We learned how regular expressions and DFAs transform source code into tokens. Understanding token precedence (e.g., keywords before identifiers) was crucial.

- **Syntax Analysis**: Implementing a recursive descent parser taught us about grammar design, operator precedence, and AST construction. We understood why left recursion must be eliminated.

- **Semantic Analysis**: Building the symbol table and type checker showed us how compilers enforce language rules. Scope management and type compatibility were challenging but rewarding.

- **Intermediate Representation**: Creating TACKY IR demonstrated how complex expressions are broken into simple three-address instructions. This abstraction separates frontend from backend concerns.

- **Optimization**: Even basic optimizations like constant folding significantly reduce code size. We gained appreciation for how production compilers achieve performance.

- **Code Generation**: Translating IR to x86-64 assembly taught us about calling conventions, register allocation, and instruction selection. The System V ABI details were intricate but essential.

### 2. Programming Skills

- **Python proficiency**: Implementing a 14,000+ line compiler improved our Python skills, especially with classes, pattern matching, and recursion.

- **Data structures**: AST representation, symbol tables (hash maps with scope chains), and instruction lists were practical applications of CS fundamentals.

- **Testing methodology**: Creating test cases that exercise edge cases taught us systematic testing approaches.

### 3. Low-Level Understanding

- **x86-64 architecture**: Register conventions, memory addressing modes, and stack frame layout are now familiar concepts.

- **Memory management**: Understanding how local variables, arrays, and structs are laid out in memory.

- **ABI compliance**: Learning why calling conventions exist and how to follow them.

---

## Challenges Faced

1. **Type System Complexity**: Handling implicit conversions, pointer arithmetic, and array decay required careful design. Integer promotion rules were particularly tricky.

2. **Parsing Expressions**: Getting operator precedence and associativity right for all operators (including ternary `?:` and assignment `=`) took multiple iterations.

3. **Register Constraints**: x86-64's two-operand instructions required careful instruction fixing. Memory-to-memory operations needed intermediate registers.

4. **Debugging IR**: When generated code crashed, tracing back through IR to find the bug was difficult. We learned to add verbose output at each phase.

---

## What We Would Improve

### Short-term Improvements
1. **Better error messages**: Include line numbers and source context in error reports
2. **More optimizations**: Implement common subexpression elimination and dead code removal
3. **Register allocation**: Use graph coloring instead of spilling everything to stack

### Long-term Improvements
1. **Support more C features**: Add `switch`, `enum`, `typedef`, and preprocessor
2. **Multiple backends**: Target ARM64 or RISC-V in addition to x86-64
3. **Debug information**: Generate DWARF debug info for use with GDB
4. **Standard library**: Implement or link a minimal C runtime

---

## Conclusion

This project transformed our understanding of how programming languages work. Before, compilers were black boxes; now we understand each transformation from source to machine code. The skills gained—parsing, type systems, code generation—are applicable far beyond compilers, from IDEs to static analyzers to domain-specific languages.

Most importantly, we learned that building complex systems requires careful planning, modular design, and systematic testing. The compiler works because each phase has clear inputs, outputs, and invariants.

---

*Total project effort: ~[X] hours across [Y] weeks*
*Lines of code: ~14,400 Python*

---

**Group Member Contributions:**

| Member | Contributions |
|--------|--------------|
| [Name 1] | [Lexer, Parser, Documentation] |
| [Name 2] | [Type Checker, IR Generation] |
| [Name 3] | [Code Generation, Testing] |

---

*[Signatures]*
