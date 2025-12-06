/* Test Case 12: Break and Continue
 * Tests: break and continue statements in loops
 * Expected return: 12 (sum of even numbers 2+4+6, stops at 7)
 */

int main(void) {
    int sum = 0;

    for (int i = 1; i <= 10; i = i + 1) {
        if (i == 7) {
            break;
        }

        if (i % 2 != 0) {
            continue;
        }

        sum = sum + i;
    }

    return sum;
}
