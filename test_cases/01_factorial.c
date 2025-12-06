/*
 * Test Case 1: Factorial Computation
 * Purpose: Demonstrates recursion, conditionals, arithmetic
 * Expected Output: Returns 120 (5!)
 */

int factorial(int n) {
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}

int main(void) {
    int result = factorial(5);
    return result;  // Expected: 120
}
