#!/bin/bash

# Input and output file paths
input_file="static/files/curated_puns.txt"
output_file="static/files/puns.csv"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found."
    exit 1
fi

# Create the output folder if it doesn't exist
mkdir -p "$(dirname "$output_file")"

# Process each line in the input file
while IFS=? read -r question answer || [ -n "$question" ]; do
    # Trim leading and trailing whitespaces
    question=$(echo "$question" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    answer=$(echo "$answer" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')

    # Append to the CSV file
    echo "$question, $answer" >> "$output_file"
done < "$input_file"

echo "CSV file '$output_file' created successfully."