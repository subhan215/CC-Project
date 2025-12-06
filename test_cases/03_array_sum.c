/*
 * Test Case 3: Array Sum with Pointers
 * Purpose: Demonstrates arrays, pointers, for loops
 * Expected Output: Returns 15 (sum of 1+2+3+4+5)
 */

int sum_array(int *arr, int size) {
    int total = 0;
    for (int i = 0; i < size; i = i + 1) {
        total = total + arr[i];
    }
    return total;
}

int main(void) {
    int numbers[5] = {1, 2, 3, 4, 5};
    int result = sum_array(numbers, 5);
    return result;  // Expected: 15
}
