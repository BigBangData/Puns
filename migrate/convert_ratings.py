def convert_line(line, new_id):
    parts = line.strip().split('|')
    # Use repr() to ensure the string is properly quoted
    return f"({new_id},{parts[1]},{parts[2]},{repr(parts[3])}),"

def convert_file(input, out):
    with open(input, 'r') as infile, open(out, 'w') as outfile:
        new_id = 1
        for line in infile:
            outfile.write(convert_line(line, new_id) + '\n')
            new_id += 1

input = 'ratings_input.txt'
out = 'ratings_output.txt'

convert_file(input, out)