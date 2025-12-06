# Mini-C Test Cases

## CS4031 - Compiler Construction | Fall 2025

---

## Test Case Summary

| # | File | Purpose | Expected Return |
|---|------|---------|-----------------|
| 1 | `01_factorial.c` | Recursion, conditionals | 120 |
| 2 | `02_fibonacci.c` | Multiple recursion | 55 |
| 3 | `03_array_sum.c` | Arrays, pointers, loops | 15 |
| 4 | `04_gcd.c` | GCD algorithm, modulo | 6 |
| 5 | `05_power.c` | Power function, recursion | 32 |
| 6 | `06_nested_loops.c` | Nested for loops | 36 |
| 7 | `07_while_loop.c` | While loop, accumulator | 55 |
| 8 | `08_do_while.c` | Do-while loop | 10 |
| 9 | `09_logical_ops.c` | AND, OR, NOT operators | 1 |
| 10 | `10_ternary.c` | Ternary operator ?: | 20 |
| 11 | `11_multiple_funcs.c` | Multiple function calls | 25 |
| 12 | `12_break_continue.c` | Break and continue | 12 |
| 13 | `13_prime_check.c` | Prime number check | 1 |

---

## Running Test Cases

### Compile and Run (Windows)

```bash
# Test Case 1: Factorial
python pcc run test_cases/01_factorial.c -o test1 && test1
echo %errorlevel%  # Should print: 120

# Test Case 4: GCD
python pcc run test_cases/04_gcd.c -o test4 && test4
echo %errorlevel%  # Should print: 6

# Test Case 13: Prime Check
python pcc run test_cases/13_prime_check.c -o test13 && test13
echo %errorlevel%  # Should print: 1
```

### Compile and Run (Linux/Mac)

```bash
# Test Case 1: Factorial
python pcc run test_cases/01_factorial.c -o factorial && ./factorial; echo $?

# Test Case 4: GCD
python pcc run test_cases/04_gcd.c -o gcd && ./gcd; echo $?
```

### View Compilation Stages

```bash
# Lexer output
python pcc --lex test_cases/01_factorial.c

# Parser output (AST)
python pcc --parse test_cases/01_factorial.c

# Semantic analysis
python pcc --validate test_cases/01_factorial.c

# Intermediate code (TACKY IR)
python pcc --tacky test_cases/01_factorial.c

# Assembly output
python pcc -S test_cases/01_factorial.c
```

---

## Test Categories

### Category 1: Recursion (Tests 1, 2, 4, 5)
- **01_factorial.c** - Basic recursion with multiplication
- **02_fibonacci.c** - Double recursion pattern
- **04_gcd.c** - Euclidean algorithm with modulo
- **05_power.c** - Exponentiation by recursion

### Category 2: Loops (Tests 3, 6, 7, 8, 12)
- **03_array_sum.c** - For loop with arrays
- **06_nested_loops.c** - Nested for loops
- **07_while_loop.c** - While loop with accumulator
- **08_do_while.c** - Do-while loop
- **12_break_continue.c** - Loop control statements

### Category 3: Operators (Tests 9, 10)
- **09_logical_ops.c** - Logical AND, OR, NOT
- **10_ternary.c** - Conditional (ternary) operator

### Category 4: Functions (Tests 11, 13)
- **11_multiple_funcs.c** - Multiple function definitions
- **13_prime_check.c** - Complex function with early returns

---

## Detailed Test Descriptions

### Test 1: Factorial
Computes 5! = 120. Tests basic recursion and conditionals.

### Test 2: Fibonacci
Computes F(10) = 55. Tests double recursion pattern.

### Test 3: Array Sum
Sums array elements: 1+2+3+4+5 = 15. Tests arrays and pointer arithmetic.

### Test 4: GCD (Greatest Common Divisor)
Computes GCD(54, 24) = 6 using Euclidean algorithm. Tests modulo operator.

### Test 5: Power
Computes 2^5 = 32. Tests recursive exponentiation.

### Test 6: Nested Loops
Computes sum of multiplication table (3x3) = 36. Tests nested loops.

### Test 7: While Loop
Computes 1+2+...+10 = 55. Tests while loop with decrement.

### Test 8: Do-While
Counts to 10. Tests do-while guarantee of at least one iteration.

### Test 9: Logical Operators
Tests &&, ||, ! operators with conditionals. Returns 1.

### Test 10: Ternary Operator
Finds max(10, 20) = 20. Tests conditional expression.

### Test 11: Multiple Functions
Tests add, subtract, multiply, divide functions. Returns 25.

### Test 12: Break and Continue
Sums even numbers up to 6 (stops at 7) = 12. Tests loop control.

### Test 13: Prime Check
Checks if 17 is prime. Returns 1 (true). Tests complex logic.

---

## Verification Script (Bash)

Save as `run_tests.sh`:

```bash
#!/bin/bash

echo "=== Mini-C Compiler Test Suite ==="
echo

tests=(
    "01_factorial:120"
    "02_fibonacci:55"
    "03_array_sum:15"
    "04_gcd:6"
    "05_power:32"
    "06_nested_loops:36"
    "07_while_loop:55"
    "08_do_while:10"
    "09_logical_ops:1"
    "10_ternary:20"
    "11_multiple_funcs:25"
    "12_break_continue:12"
    "13_prime_check:1"
)

passed=0
failed=0

for test in "${tests[@]}"; do
    name="${test%%:*}"
    expected="${test##*:}"

    echo -n "Testing $name... "
    python pcc run "test_cases/${name}.c" -o "test_cases/${name}" 2>/dev/null

    if [ -f "test_cases/${name}" ]; then
        ./test_cases/${name}
        result=$?

        if [ "$result" -eq "$expected" ]; then
            echo "PASSED (returned $result)"
            ((passed++))
        else
            echo "FAILED (returned $result, expected $expected)"
            ((failed++))
        fi
        rm "test_cases/${name}"
    else
        echo "FAILED (compilation error)"
        ((failed++))
    fi
done

echo
echo "=== Results: $passed passed, $failed failed ==="
```

---

## Verification Script (Windows Batch)

Save as `run_tests.bat`:

```batch
@echo off
echo === Mini-C Compiler Test Suite ===
echo.

setlocal enabledelayedexpansion
set passed=0
set failed=0

for %%t in (
    "01_factorial:120"
    "02_fibonacci:55"
    "03_array_sum:15"
    "04_gcd:6"
    "05_power:32"
    "06_nested_loops:36"
    "07_while_loop:55"
    "08_do_while:10"
    "09_logical_ops:1"
    "10_ternary:20"
    "11_multiple_funcs:25"
    "12_break_continue:12"
    "13_prime_check:1"
) do (
    for /f "tokens=1,2 delims=:" %%a in (%%t) do (
        echo Testing %%a...
        python pcc run test_cases\%%a.c -o test_cases\%%a.exe 2>nul
        if exist test_cases\%%a.exe (
            test_cases\%%a.exe
            if !errorlevel! equ %%b (
                echo   PASSED
                set /a passed+=1
            ) else (
                echo   FAILED - expected %%b, got !errorlevel!
                set /a failed+=1
            )
            del test_cases\%%a.exe
        ) else (
            echo   FAILED - compilation error
            set /a failed+=1
        )
    )
)

echo.
echo === Results: %passed% passed, %failed% failed ===
```

---

*These 13 test cases comprehensively demonstrate all features of the Mini-C compiler.*
