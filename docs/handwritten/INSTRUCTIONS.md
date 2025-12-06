# Handwritten Artifacts Instructions

## CS4031 - Compiler Construction | Fall 2025

---

## ⚠️ IMPORTANT: You MUST Submit These By Hand

The project requires **three handwritten artifacts** (scan/photo acceptable).

**See `COPY_TO_PAPER.md` for ready-to-copy content!**

---

## Required Documents (3 Total)

| # | Document | What to Draw |
|---|----------|--------------|
| 1 | **DFA / Transition Table** | State machine for lexer |
| 2 | **Parse Tree 1** | Factorial function derivation |
| 3 | **Parse Tree 2** | Prime check with for loop |
| 4 | **Symbol Table** | 3 scopes with variables |

---

## Step-by-Step Instructions

### Step 1: Get Paper and Pen
- Use A4 or Letter size paper
- Use black/blue pen (not pencil)
- Optional: ruler for straight lines, colored pens

### Step 2: Open COPY_TO_PAPER.md
- Open the file `docs/handwritten/COPY_TO_PAPER.md`
- This has EVERYTHING ready to copy

### Step 3: Copy Page by Page

#### PAGE 1: DFA / Transition Table
1. Write title: "LEXICAL ANALYSIS - DFA AND TRANSITION TABLE"
2. Draw the Identifier DFA (circles and arrows)
3. Draw the Integer DFA
4. Draw the Operator DFAs
5. Copy the Transition Table (use ruler for boxes)

#### PAGE 2: Parse Tree 1 - Factorial
1. Write title: "SYNTAX ANALYSIS - PARSE TREE DERIVATION 1"
2. Write the source code
3. Draw the tree structure (boxes connected by lines)
4. Write derivation steps

#### PAGE 3: Parse Tree 2 - Prime Check
1. Write title: "SYNTAX ANALYSIS - PARSE TREE DERIVATION 2"
2. Write the source code
3. Draw the more complex tree with for loop
4. Write grammar rules used

#### PAGE 4: Symbol Table
1. Write title: "SEMANTIC ANALYSIS - SYMBOL TABLE WITH SCOPE"
2. Write the source code being analyzed
3. Draw 3 tables (Global, gcd function, main function)
4. Draw scope hierarchy diagram
5. Add type checking examples

### Step 4: Sign and Date
- Write your name on each page
- Write the date
- Number pages (Page 1 of 4, etc.)

### Step 5: Scan or Photograph
- Scan to PDF, OR
- Take clear photos (good lighting, no shadows)
- Name files:
  - `01_DFA_transition_table.pdf`
  - `02_parse_tree_factorial.pdf`
  - `03_parse_tree_prime.pdf`
  - `04_symbol_table.pdf`

---

## What Each Document Should Show

### 1. DFA / Transition Table

**Must Include:**
- Start state (arrow pointing to q0)
- Accept states (double circles)
- Transitions with labels
- DFA for: identifiers, integers, operators

**Example tokens to show:**
```
int      → keyword
factorial → identifier
123      → integer constant
123L     → long constant
<=       → less_or_equal operator
==       → equal operator
&&       → and operator
```

---

### 2. Parse Tree Derivation 1 (Factorial)

**Source Code:**
```c
int factorial(int n) {
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}
```

**Must Show:**
- Function declaration at root
- Parameter list
- If statement with condition
- Return statements
- Recursive call

---

### 3. Parse Tree Derivation 2 (Prime Check)

**Source Code:**
```c
int is_prime(int n) {
    if (n <= 1)
        return 0;
    for (int i = 2; i * i <= n; i = i + 1) {
        if (n % i == 0)
            return 0;
    }
    return 1;
}
```

**Must Show:**
- For loop structure (init, condition, update, body)
- Nested if statement
- Complex expressions (i * i <= n)
- Modulo operation (n % i)

---

### 4. Symbol Table with Scope

**Source Code:**
```c
int result = 0;

int gcd(int a, int b) {
    if (b == 0) {
        return a;
    }
    int temp = a % b;
    return gcd(b, temp);
}

int main(void) {
    int x = 48;
    int y = 18;
    result = gcd(x, y);
    return result;
}
```

**Must Show:**
- 3 scope levels (global, gcd, main)
- Variable types and storage
- Scope parent pointers
- How lookup works

---

## Tips for Good Handwritten Documents

1. ✅ **Use rulers** for table lines
2. ✅ **Write clearly** - must be readable
3. ✅ **Double circles** for accept states in DFA
4. ✅ **Label everything** - don't assume reader knows
5. ✅ **Draw arrows clearly** - show direction
6. ✅ **Box each table** - neat presentation
7. ✅ **Add legends** - explain symbols used

---

## File Naming After Scanning

Place files in this folder:
```
docs/handwritten/
├── INSTRUCTIONS.md          (this file)
├── COPY_TO_PAPER.md        (content to copy)
├── 01_DFA_transition_table.pdf
├── 02_parse_tree_factorial.pdf
├── 03_parse_tree_prime.pdf
└── 04_symbol_table.pdf
```

---

## Quick Reference: What Instructor Looks For

| Document | Key Points |
|----------|------------|
| DFA | States, transitions, accept states clearly marked |
| Parse Tree 1 | Correct tree structure for recursion |
| Parse Tree 2 | Handles loops and complex expressions |
| Symbol Table | Shows scope nesting and lookup |

---

**Time Estimate:** 1-2 hours to write all 4 pages

**Remember:** These are the ONLY handwritten documents required. Everything else is typed/printed!
