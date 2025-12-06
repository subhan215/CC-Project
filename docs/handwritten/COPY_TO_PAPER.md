# HANDWRITTEN ARTIFACTS - COPY TO PAPER

## CS4031 - Compiler Construction | Fall 2025
## Mini-C Compiler (PCC)

---

# PAGE 1: DFA / TRANSITION TABLE FOR LEXICAL ANALYSIS

## Title (write at top):
```
LEXICAL ANALYSIS - DFA AND TRANSITION TABLE
Mini-C Compiler | CS4031
```

---

## SECTION A: IDENTIFIER AND KEYWORD DFA

Draw this state diagram:

```
                        letter or digit or _
                          ┌─────────────┐
                          │             │
                          ▼             │
START ──► ( q0 ) ──letter or _──► (( q1 )) ◄───┘
           │                      ACCEPT:ID
           │
           └── other ──► ERROR


States:
  q0 = Start state
  q1 = Accept state (IDENTIFIER or KEYWORD)

After accepting, check if lexeme matches keyword list:
  Keywords: int, void, return, if, else, while, for,
            do, break, continue, long, char, double,
            unsigned, signed, struct, sizeof, static, extern

If match → return KEYWORD token
Else → return IDENTIFIER token
```

---

## SECTION B: INTEGER CONSTANT DFA

Draw this state diagram:

```
                    digit [0-9]
                   ┌──────────┐
                   │          │
                   ▼          │
START ──► ( q0 ) ──digit──► (( q1 )) ◄──┘
                            ACCEPT:INT
                               │
                    ┌──────────┼───────────┐
                    │          │           │
                    ▼          ▼           ▼
                  'u'/'U'    'l'/'L'      other
                    │          │           │
                    ▼          ▼           ▼
                (( q2 ))    (( q3 ))   ACCEPT:INT
               ACCEPT:UINT  ACCEPT:LONG
                    │          │
                    │          │
                    ▼          ▼
                  'l'/'L'    'u'/'U'
                    │          │
                    ▼          ▼
                (( q4 ))    (( q4 ))
               ACCEPT:ULONG ACCEPT:ULONG

Token Types:
  INT   = 123
  UINT  = 123u or 123U
  LONG  = 123l or 123L
  ULONG = 123ul or 123UL
```

---

## SECTION C: OPERATOR DFAs

### Comparison Operators:

```
    START ──► ( q0 )
                │
     ┌──────┬──┴───┬──────┬──────┐
     │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼
    '<'    '>'    '='    '!'    '&'
     │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼
   (q1)   (q2)   (q3)   (q4)   (q5)
     │      │      │      │      │
  ┌──┴──┐ ┌┴──┐ ┌─┴─┐ ┌─┴─┐  ┌─┴─┐
  │     │ │   │ │   │ │   │  │   │
  ▼     ▼ ▼   ▼ ▼   ▼ ▼   ▼  ▼   ▼
 '='  other'=' other'=' other'=' other'&' other
  │     │  │   │  │   │  │   │   │    │
  ▼     ▼  ▼   ▼  ▼   ▼  ▼   ▼   ▼    ▼
((<=)) ((<))((>=))((>))((==))((=))((!))((!=))((&&))((&))
```

### Summary Table:
```
Input  │ Token
───────┼────────
  <    │ LESS_THAN
  <=   │ LESS_OR_EQUAL
  >    │ GREATER_THAN
  >=   │ GREATER_OR_EQUAL
  =    │ ASSIGN
  ==   │ EQUAL
  !    │ NOT
  !=   │ NOT_EQUAL
  &    │ AMPERSAND
  &&   │ AND
  |    │ PIPE
  ||   │ OR
```

---

## SECTION D: COMPLETE TRANSITION TABLE

```
┌───────┬───────┬───────┬─────┬─────┬─────┬─────┬─────┬────────┐
│ State │ a-z   │ 0-9   │  <  │  =  │  !  │  &  │  |  │ other  │
│       │ A-Z _ │       │     │     │     │     │     │        │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q0   │  q1   │  q2   │ q3  │ q4  │ q5  │ q6  │ q7  │ single │
│ START │ IDENT │ NUM   │     │     │     │     │     │  char  │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q1   │  q1   │  q1   │ ACC │ ACC │ ACC │ ACC │ ACC │  ACC   │
│ IDENT │ loop  │ loop  │ ID  │ ID  │ ID  │ ID  │ ID  │  ID    │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q2   │ ACC   │  q2   │ ACC │ ACC │ ACC │ ACC │ ACC │  ACC   │
│  NUM  │ INT   │ loop  │ INT │ INT │ INT │ INT │ INT │  INT   │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q3   │ ACC   │ ACC   │ ACC │ q8  │ ACC │ ACC │ ACC │  ACC   │
│  '<'  │  <    │  <    │  <  │ <=  │  <  │  <  │  <  │   <    │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q4   │ ACC   │ ACC   │ ACC │ q9  │ ACC │ ACC │ ACC │  ACC   │
│  '='  │  =    │  =    │  =  │ ==  │  =  │  =  │  =  │   =    │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q5   │ ACC   │ ACC   │ ACC │ q10 │ ACC │ ACC │ ACC │  ACC   │
│  '!'  │  !    │  !    │  !  │ !=  │  !  │  !  │  !  │   !    │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q6   │ ACC   │ ACC   │ ACC │ ACC │ ACC │ q11 │ ACC │  ACC   │
│  '&'  │  &    │  &    │  &  │  &  │  &  │ &&  │  &  │   &    │
├───────┼───────┼───────┼─────┼─────┼─────┼─────┼─────┼────────┤
│  q7   │ ACC   │ ACC   │ ACC │ ACC │ ACC │ ACC │ q12 │  ACC   │
│  '|'  │  |    │  |    │  |  │  |  │  |  │  |  │ ||  │   |    │
└───────┴───────┴───────┴─────┴─────┴─────┴─────┴─────┴────────┘

Legend:
  q0-q12 = States
  ACC    = Accept (emit token and return to q0)
  loop   = Stay in current state
  single = Single character tokens: ( ) { } ; , + - * / %
```

---

# PAGE 2: PARSE TREE DERIVATION 1 - FACTORIAL FUNCTION

## Title (write at top):
```
SYNTAX ANALYSIS - PARSE TREE DERIVATION 1
Factorial Function | Mini-C Compiler
```

---

## Source Code:
```c
int factorial(int n) {
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}
```

---

## Parse Tree (draw this):

```
                              Program
                                 │
                                 ▼
                             FunDecl
                    ┌────────────┼────────────────┐
                    │            │                │
                    ▼            ▼                ▼
               ReturnType     Name            Parameters
                  int      factorial          (int n)
                                                 │
                                                 ▼
                                              ParamInfo
                                              ┌────┴────┐
                                              │         │
                                             int        n
                                 │
                                 ▼
                               Body
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
                 IfStmt                   ReturnStmt
            ┌──────┼──────┐                   │
            │      │      │                   ▼
            ▼      ▼      ▼               Binary(*)
         Cond   Then    Else             ┌────┴────┐
           │      │    (none)            │         │
           ▼      ▼                      ▼         ▼
      Binary(<=) ReturnStmt            Var(n)  FunctionCall
      ┌────┴────┐    │                         ┌────┴────┐
      │         │    ▼                         │         │
      ▼         ▼  Const(1)                factorial  Args
    Var(n)  Const(1)                                    │
                                                        ▼
                                                   Binary(-)
                                                   ┌────┴────┐
                                                   │         │
                                                   ▼         ▼
                                                 Var(n)  Const(1)
```

---

## Derivation Steps (Leftmost Derivation):

```
Step 1:  Program
         → FunDecl

Step 2:  FunDecl
         → Type Identifier ( Params ) Block

Step 3:  Type Identifier ( Params ) Block
         → int factorial ( ParamList ) { BlockItems }

Step 4:  int factorial ( ParamList ) { BlockItems }
         → int factorial ( int n ) { BlockItems }

Step 5:  { BlockItems }
         → { Statement Statement }

Step 6:  { Statement Statement }
         → { IfStmt ReturnStmt }

Step 7:  { IfStmt ReturnStmt }
         → { if ( Expr ) Statement return Expr ; }

Step 8:  { if ( Expr ) Statement return Expr ; }
         → { if ( n <= 1 ) return 1 ; return n * factorial(n-1) ; }
```

---

# PAGE 3: PARSE TREE DERIVATION 2 - PRIME CHECK WITH FOR LOOP

## Title (write at top):
```
SYNTAX ANALYSIS - PARSE TREE DERIVATION 2
Prime Check Function | Mini-C Compiler
```

---

## Source Code:
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

---

## Parse Tree (draw this):

```
                                    Program
                                       │
                                       ▼
                                   FunDecl
                          ┌────────────┼────────────┐
                          │            │            │
                         int       is_prime     (int n)
                                       │
                                       ▼
                                     Body
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
                 IfStmt             ForStmt          ReturnStmt
                    │                  │                  │
            ┌───────┴───────┐          │              Const(1)
            │               │          │
         Cond            Then          │
            │               │          │
            ▼               ▼          │
       Binary(<=)     ReturnStmt       │
       ┌────┴────┐         │          │
      Var(n)  Const(1)  Const(0)      │
                                       │
                                       ▼
                          ┌────────────┼────────────────┬─────────┐
                          │            │                │         │
                         Init        Cond             Post      Body
                          │            │                │         │
                          ▼            ▼                ▼         ▼
                      VarDecl    Binary(<=)      Assignment   IfStmt
                     int i = 2   ┌────┴────┐     i = i + 1      │
                              Binary(*)  Var(n)            ┌────┴────┐
                              ┌──┴──┐                    Cond     Then
                           Var(i) Var(i)                   │         │
                                                           ▼         ▼
                                                    Binary(==)  Return(0)
                                                    ┌────┴────┐
                                                 Binary(%)  Const(0)
                                                 ┌────┴────┐
                                              Var(n)    Var(i)
```

---

## Grammar Rules Used:

```
Program      → Declaration*
Declaration  → FunDecl | VarDecl
FunDecl      → Type Identifier ( Params ) Block
Block        → { BlockItem* }
BlockItem    → Statement | Declaration
Statement    → ReturnStmt | IfStmt | ForStmt | ExprStmt
ReturnStmt   → return Expr? ;
IfStmt       → if ( Expr ) Statement (else Statement)?
ForStmt      → for ( ForInit? ; Expr? ; Expr? ) Statement
ForInit      → VarDecl | Expr
Expr         → Assignment | Conditional | Binary | Unary | Primary
Binary       → Expr BinOp Expr
BinOp        → + | - | * | / | % | < | <= | > | >= | == | != | && | ||
Primary      → Identifier | Constant | ( Expr ) | FunctionCall
```

---

# PAGE 4: SYMBOL TABLE WITH SCOPE EXAMPLE

## Title (write at top):
```
SEMANTIC ANALYSIS - SYMBOL TABLE WITH SCOPE
Mini-C Compiler | CS4031
```

---

## Source Code Being Analyzed:
```c
int result = 0;                    // Global scope

int gcd(int a, int b) {            // Function scope
    if (b == 0) {                  // Block scope 1
        return a;
    }
    int temp = a % b;              // Still in function scope
    return gcd(b, temp);
}

int main(void) {                   // Function scope
    int x = 48;                    // Local to main
    int y = 18;                    // Local to main
    result = gcd(x, y);
    return result;
}
```

---

## SYMBOL TABLE (draw these boxes):

### SCOPE 0: GLOBAL SCOPE
```
┌────────────────────────────────────────────────────────────────────┐
│  SCOPE LEVEL 0 - GLOBAL                                            │
├──────────┬────────────────┬──────────┬─────────┬───────────────────┤
│   Name   │     Type       │ Storage  │ Defined │      Notes        │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│  result  │     int        │  Global  │   Yes   │  Initialized = 0  │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│   gcd    │ int(int, int)  │  Global  │   Yes   │  Function         │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│   main   │ int(void)      │  Global  │   Yes   │  Function         │
└──────────┴────────────────┴──────────┴─────────┴───────────────────┘
```

### SCOPE 1: FUNCTION gcd
```
┌────────────────────────────────────────────────────────────────────┐
│  SCOPE LEVEL 1 - FUNCTION: gcd                                     │
│  Parent Scope: 0 (Global)                                          │
├──────────┬────────────────┬──────────┬─────────┬───────────────────┤
│   Name   │     Type       │ Storage  │ Offset  │      Notes        │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│    a     │     int        │  Param   │  %edi   │  1st parameter    │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│    b     │     int        │  Param   │  %esi   │  2nd parameter    │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│   temp   │     int        │  Local   │ -4(%rbp)│  Local variable   │
└──────────┴────────────────┴──────────┴─────────┴───────────────────┘
```

### SCOPE 2: FUNCTION main
```
┌────────────────────────────────────────────────────────────────────┐
│  SCOPE LEVEL 1 - FUNCTION: main                                    │
│  Parent Scope: 0 (Global)                                          │
├──────────┬────────────────┬──────────┬─────────┬───────────────────┤
│   Name   │     Type       │ Storage  │ Offset  │      Notes        │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│    x     │     int        │  Local   │ -4(%rbp)│  Initialized = 48 │
├──────────┼────────────────┼──────────┼─────────┼───────────────────┤
│    y     │     int        │  Local   │ -8(%rbp)│  Initialized = 18 │
└──────────┴────────────────┴──────────┴─────────┴───────────────────┘
```

---

## SCOPE HIERARCHY DIAGRAM:

```
                    ┌─────────────────────────┐
                    │   GLOBAL SCOPE (0)      │
                    │   - result: int         │
                    │   - gcd: function       │
                    │   - main: function      │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
              ▼                                   ▼
   ┌──────────────────────┐          ┌──────────────────────┐
   │  FUNCTION gcd (1)    │          │  FUNCTION main (1)   │
   │  - a: int (param)    │          │  - x: int (local)    │
   │  - b: int (param)    │          │  - y: int (local)    │
   │  - temp: int (local) │          └──────────────────────┘
   └──────────────────────┘

   Lookup Order:
   ─────────────
   When resolving 'result' in main:
   1. Check main's scope → NOT FOUND
   2. Check parent (global) → FOUND (result: int)

   When resolving 'a' in gcd:
   1. Check gcd's scope → FOUND (a: int, parameter)
```

---

## TYPE CHECKING EXAMPLES:

```
Expression: gcd(x, y)
─────────────────────
1. Lookup 'gcd' → Found: int(int, int)
2. Lookup 'x' → Found: int ✓ matches param 1
3. Lookup 'y' → Found: int ✓ matches param 2
4. Return type: int ✓

Expression: a % b
─────────────────
1. Lookup 'a' → Found: int
2. Lookup 'b' → Found: int
3. Operator '%' requires: int, int → produces int ✓

Expression: result = gcd(x, y)
──────────────────────────────
1. LHS 'result' → int
2. RHS 'gcd(x,y)' → int
3. Assignment int = int ✓
```

---

## STORAGE ALLOCATION (x86-64):

```
Function: gcd
─────────────
Parameters (System V ABI):
  %edi ← a (1st int parameter)
  %esi ← b (2nd int parameter)

Stack Frame:
  ┌──────────────────┐  High Address
  │   Return Addr    │
  ├──────────────────┤  ← %rbp (after push)
  │   Saved %rbp     │
  ├──────────────────┤
  │   temp (4 bytes) │  ← -4(%rbp)
  ├──────────────────┤
  │   (padding)      │  ← -8(%rbp)
  └──────────────────┘  Low Address ← %rsp
```

---

# PAGE 5: ADDITIONAL NOTES (OPTIONAL)

## Token List Reference:
```
KEYWORDS:    int, void, return, if, else, while, for, do,
             break, continue, long, char, double, unsigned,
             signed, struct, sizeof, static, extern

OPERATORS:   + - * / % < > <= >= == != && || ! &
             = ( ) { } [ ] ; , ? :

LITERALS:    INTEGER: [0-9]+
             IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*
```

## Type System:
```
Primitive Types: int, long, char, double, void
Derived Types:   pointer (*), array ([])

Type Compatibility:
  int ↔ long (implicit conversion)
  int ↔ char (implicit conversion)
  T* + int → T* (pointer arithmetic)
  T[] → T* (array decay)
```

---

## Signatures:

```
Prepared by: _______________________

Date: _______________________

Group Members:
  1. _______________________
  2. _______________________
  3. _______________________
  4. _______________________
  5. _______________________
  6. _______________________
```
