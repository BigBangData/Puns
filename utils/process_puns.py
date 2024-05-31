import os
import csv

# Create paths for I/O
base_dir = os.path.join('static', 'files')
input_file_path = os.path.join(base_dir, 'curated_puns.txt')
output_file_path = os.path.join(base_dir, 'puns.csv')

# Check if the input file exists
# if it does, open input file context handler
# if it does not, error out
try:
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        input_lines = input_file.readlines()
except FileNotFoundError:
    print(f"Error: Input file '{input_file_path}' not found.")
    exit(1)

# Open output file context handler
with open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
    # Start CSV writer
    csv_writer = csv.writer(output_file)
    # Create header
    csv_writer.writerow(['question', 'answer'])
    # Process each line in the input file
    for ix, line in enumerate(input_lines):
        # Split the line into question and answer
        try:
            question, answer = line.split('?', 1)
        except ValueError as e:
            try:
                question, answer = line.split('...', 1)
            except ValueError as e:
                print(f"Line {ix} did not split.")
                print(f"Content: {line}")
                continue
        # Trim leading and trailing whitespaces
        question = question.strip()
        answer = answer.strip()
        # Replace commas in the text with a placeholder
        question = question.replace(',', '<<COMMA>>')
        answer = answer.replace(',', '<<COMMA>>')
        # Replace right-quotation marks with regular apostrophes
        question = question.replace('’', "'")
        answer = answer.replace('’', "'")
        # Replace the placeholder back with a regular comma
        question = question.replace('<<COMMA>>', ',')
        answer = answer.replace('<<COMMA>>', ',')
        # Write to the CSV file
        csv_writer.writerow([question, answer])

print(f"CSV file '{output_file_path}' created successfully.")