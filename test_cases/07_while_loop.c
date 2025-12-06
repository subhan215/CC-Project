/* Test Case 07: While Loop
 * Tests: While loop, decrement, accumulator pattern
 * Expected return: 55 (sum of 1 to 10)
 */

int main(void) {
    int n = 10;
    int sum = 0;

    while (n > 0) {
        sum = sum + n;
        n = n - 1;
    }

    return sum;
}
