#!/bin/bash

# Run the C program and capture the output
output=$(./ev_sensor_orig)

# Extract the random value using grep and awk
random_value=$(echo "$output" | grep -oP '\d+')

# Decrease the value by 10, ensuring it does not go below zero
decreased_value=$((random_value - 4))

# Ensure the decreased value is not below zero
if [ $decreased_value -lt 0 ]; then
    decreased_value=0
fi

echo $decreased_value
