/* Test Case 10: Ternary Operator
 * Tests: Conditional (ternary) operator ?:
 * Expected return: 20 (max of 10 and 20)
 */

int max(int a, int b) {
    return a > b ? a : b;
}

int min(int a, int b) {
    return a < b ? a : b;
}

int main(void) {
    int x = 10;
    int y = 20;
    return max(x, y);
}
