import os
import csv

# Create paths for I/O
base_dir = os.path.join('static', 'files')
input_file_path = os.path.join(base_dir, 'curated_puns.txt')
output_file_path = os.path.join(base_dir, 'puns.csv')

# Check if the input file exists
# if it does, open input file context handler, else error out
try:
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        input_lines = input_file.readlines()
except FileNotFoundError:
    print(f"Error: Input file '{input_file_path}' not found.")
    exit(1)

# Function to convert pipe-delimited file to CSV
def convert_pipe_to_csv(input_file_path, output_file_path):
    with open(input_file_path, 'r', newline='', encoding='utf-8') as infile, \
        open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
        # read the pipe-delimited file
        reader = csv.reader(infile, delimiter='|')
        # write to the CSV file
        writer = csv.writer(outfile)
        # create a header
        writer.writerow(['question', 'answer', 'blame'])
        for row in reader:
            # jandle cases where the row has fewer columns than expected
            if len(row) < 3:
                row += [''] * (3 - len(row))  # add empty strings to make the row length 3
            writer.writerow(row)

# convert the file
convert_pipe_to_csv(input_file_path, output_file_path)
print(f"CSV file '{output_file_path}' created successfully.")