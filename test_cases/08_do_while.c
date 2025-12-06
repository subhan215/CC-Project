/* Test Case 08: Do-While Loop
 * Tests: Do-while loop construct
 * Expected return: 10 (counts up to 10)
 */

int main(void) {
    int count = 0;

    do {
        count = count + 1;
    } while (count < 10);

    return count;
}
