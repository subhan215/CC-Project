/* Test Case 09: Logical Operators
 * Tests: AND (&&), OR (||), NOT (!)
 * Expected return: 1 (true)
 */

int main(void) {
    int a = 5;
    int b = 10;
    int c = 0;

    int result = 0;

    if (a > 0 && b > 0) {
        result = result + 1;
    }

    if (a > 100 || b > 5) {
        result = result + 1;
    }

    if (!c) {
        result = result - 1;
    }

    return result;
}
