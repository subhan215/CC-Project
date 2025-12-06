/* Test Case 11: Multiple Functions
 * Tests: Multiple function definitions, function calls
 * Expected return: 25 (5 + 10 + 10)
 */

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int multiply(int a, int b) {
    return a * b;
}

int divide(int a, int b) {
    return a / b;
}

int main(void) {
    int a = 20;
    int b = 10;

    int sum = add(a, b);
    int diff = subtract(a, b);
    int prod = multiply(a, b);
    int quot = divide(a, b);

    return subtract(sum, diff) + quot;
}
