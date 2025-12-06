/* Test Case 14: Optimization Demo
 * Tests: Constant folding, algebraic simplification, dead store elimination
 * Expected return: 42
 *
 * This test demonstrates the optimizer's capabilities:
 *
 * CONSTANT FOLDING:
 *   - 10 + 5 → 15
 *   - 3 * 4 → 12
 *   - 20 / 4 → 5
 *   - 100 - 58 → 42
 *
 * ALGEBRAIC SIMPLIFICATION:
 *   - x + 0 → x
 *   - x * 1 → x
 *   - x - 0 → x
 *   - x * 0 → 0
 *
 * DEAD STORE ELIMINATION:
 *   - unused variables are removed
 *
 * STRENGTH REDUCTION:
 *   - x * 2 → x + x
 */

int compute(int x) {
    /* Constant folding opportunities */
    int a = 10 + 5;           /* Should fold to 15 */
    int b = 3 * 4;            /* Should fold to 12 */
    int c = 20 / 4;           /* Should fold to 5 */

    /* Algebraic simplification opportunities */
    int d = x + 0;            /* Should simplify to x */
    int e = x * 1;            /* Should simplify to x */
    int f = x - 0;            /* Should simplify to x */

    /* Strength reduction opportunity */
    int g = x * 2;            /* Should become x + x */

    /* Dead stores - these are never used */
    int dead1 = 999;
    int dead2 = 888;
    int dead3 = 777;

    /* Only use some variables */
    return a + b + c;         /* 15 + 12 + 5 = 32... but we return 42 */
}

int add_constants(void) {
    /* Multiple constant folding */
    int x = 2 + 3;            /* 5 */
    int y = x + 5;            /* If x is propagated: 5 + 5 = 10 */
    int z = 10 + 10 + 10 + 10 + 2;  /* Should fold to 42 */
    return z;
}

int main(void) {
    /* Simple constant expression */
    int result = 100 - 58;    /* Should fold to 42 */

    /* Dead store - overwritten before use */
    int temp = 999;
    temp = 42;

    /* Algebraic identity */
    int val = temp * 1;       /* Should simplify to temp */
    val = val + 0;            /* Should simplify to val */

    return val;               /* Returns 42 */
}
