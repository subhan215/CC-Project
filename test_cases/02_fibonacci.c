/*
 * Test Case 2: Fibonacci Sequence
 * Purpose: Demonstrates recursion, multiple return paths
 * Expected Output: Returns 55 (10th Fibonacci number)
 */

int fibonacci(int n) {
    if (n <= 0)
        return 0;
    if (n == 1)
        return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main(void) {
    int result = fibonacci(10);
    return result;  // Expected: 55
}
