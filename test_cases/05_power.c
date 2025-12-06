/* Test Case 05: Power Function
 * Tests: Recursion, multiplication, base cases
 * Expected return: 32 (2^5)
 */

int power(int base, int exp) {
    if (exp == 0)
        return 1;
    return base * power(base, exp - 1);
}

int main(void) {
    return power(2, 5);
}
