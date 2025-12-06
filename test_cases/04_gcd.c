/* Test Case 04: Greatest Common Divisor (GCD)
 * Tests: Recursion, modulo operator, conditionals
 * Expected return: 6 (GCD of 54 and 24)
 */

int gcd(int a, int b) {
    if (b == 0)
        return a;
    return gcd(b, a % b);
}

int main(void) {
    return gcd(54, 24);
}
