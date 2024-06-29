def count_lines(file_path):
    with open(file_path, 'r') as file:
        line_count = sum(1 for line in file)
    return line_count

def convert_line(line, new_id):
    parts = line.strip().split('|')
    # Use repr() to ensure the string is properly quoted
    return f"({new_id},{parts[1]},{parts[2]},{repr(parts[3])})"

def convert_file(input, out):
    n_lines = count_lines(input) -1 # to account for header
    with open(input, 'r') as infile, open(out, 'w') as outfile:
        new_id = 0
        for line in infile:
            row = convert_line(line, new_id)
            if new_id == 0:
                outfile.write(f'INSERT INTO ratings (id, user_id, pun_id, rating) VALUES \n')
            elif new_id < n_lines:
                outfile.write(', '.join([row, '\n']))
            else: 
                outfile.write('; '.join([row, '\n']))
            new_id += 1

if __name__=="__main__":
    input = 'ratings_input.txt'
    out = 'ratings_insert.sql'
    convert_file(input, out)