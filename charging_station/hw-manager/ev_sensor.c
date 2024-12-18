#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Function to generate a random number between min and max (inclusive)
int getRandomValue(int min, int max) {
    return rand() % (max - min + 1) + min;
}

int main() {
    // Set the seed for the random number generator
    srand(time(NULL));

    // Define the range
    int min = 28;  // Minimum value
    int max = 36; // Maximum value

    // Generate a random value
    int randomValue = getRandomValue(min, max);
    printf("%d", randomValue);

    return 0;
}