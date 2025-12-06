/* Test Case 13: Prime Number Check
 * Tests: Complex logic, early return, loops
 * Expected return: 1 (17 is prime)
 */

int is_prime(int n) {
    if (n <= 1)
        return 0;
    if (n <= 3)
        return 1;
    if (n % 2 == 0)
        return 0;

    for (int i = 3; i * i <= n; i = i + 2) {
        if (n % i == 0)
            return 0;
    }

    return 1;
}

int main(void) {
    return is_prime(17);
}
