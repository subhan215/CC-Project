/* Test Case 06: Nested Loops
 * Tests: Nested for loops, multiplication table logic
 * Expected return: 45 (sum of 1+2+3+...+9 using nested loop pattern)
 */

int main(void) {
    int sum = 0;
    for (int i = 1; i <= 3; i = i + 1) {
        for (int j = 1; j <= 3; j = j + 1) {
            sum = sum + i * j;
        }
    }
    return sum;
}
