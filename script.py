import time
import os
import sys

# Function to read Sudoku board from a text file
def read_board(file_path):
    try:
        with open(file_path, 'r') as file:
            puzzle = [[int(num) for num in line.split()] for line in file]
        return puzzle, len(puzzle)
    except FileNotFoundError:
        print("----> File not found <----")

# Function to print the Sudoku board to the console
def print_board(board):
    for row in board:
        print(" ".join(str(num) for num in row))
    print()

# Function to write the solved Sudoku board to an output text file
def write_output_to_file(board, input_file_path):
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    base_name = os.path.basename(input_file_path)
    output_file_path = os.path.join("outputs", base_name.replace(".txt", "_output.txt"))
    
    with open(output_file_path, 'w') as file:
        for row in board:
            line = " ".join(str(num) for num in row)
            file.write(line + "\n")

    return output_file_path

# Find the next empty space in Sudoku board and return its positions
def find_empty(board, size):
    for row in range(size):
        for col in range(size):
            if board[row][col] == 0 :
                return row,col
    return None

# Check whether a specific number can be placed at a given position
def is_valid(board, num, pos, size):
    row, col = pos

    # Check if the number exists in the same row
    for j in range(size):
        if board[row][j] == num:
            return False

    # Check if the number exists in the same column
    for i in range(size):
        if board[i][col] == num:
            return False
        
    # Check if the number exists in the same block
    subgrid_size = int(size ** 0.5)
    row_block_start = subgrid_size* (row // subgrid_size)
    col_block_start = subgrid_size* (col // subgrid_size)
    row_block_end = row_block_start + subgrid_size
    col_block_end = col_block_start + subgrid_size

    for i in range(row_block_start, row_block_end):
        for j in range(col_block_start, col_block_end):
            if board[i][j] == num:
                return False

    return True

# Function to solve the Sudoku puzzle using backtracking algorithm
def solve(board, cache,size):
    blank = find_empty(board, size)
    if not blank:
        return True
    else:
        row, col = blank

    for value in cache[(row,col)]:
        if is_valid(board, value, blank, size):
            board[row][col] = value

            if solve(board, cache,size):
                return True

            board[row][col] = 0
    return False

# Find allowed values for a specific position
def find_allowed_values(board,row,col, size):
    numbers_list = list()
    subgrid_size = int(size ** 0.5)

    for number in range(1, size+1):
        found = False
        # Check if the number exists in the same row
        for j in range(size):
            if board[row][j] == number:
                found = True
                break
        # Check if the number exists in the same column
        if found == True:
            continue
        else:
            for i in range(size):
                if board[i][col] == number:
                    found = True
                    break

        # Check if the number exists in the same block
        if found == True:
            continue
        else:
            row_block_start = subgrid_size* (row // subgrid_size)
            col_block_start = subgrid_size* (col // subgrid_size)

            row_block_end = row_block_start + subgrid_size
            col_block_end = col_block_start + subgrid_size
            for i in range(row_block_start, row_block_end):
                for j in range(col_block_start, col_block_end):
                    if board[i][j] == number:
                        found = True
                        break
        if found == False:
            numbers_list.append(number)
    return numbers_list

# Function to find legitimate values for each individual cell and Store in a dictionary
def find_valid_cache_values(board, size):
    cache = dict()
    for i in range(size):
        for j in range(size):
            if board[i][j] == 0:
                cache[(i,j)] = find_allowed_values(board,i,j, size)
    return cache

# Order the cache values based on their appearance frequency
def order_valid_cache_values(board, cache_values, size):
    subgrid_size = int(size ** 0.5)

    cache_priority = dict()
    count_appearance_row = [dict() for i in range(size)]
    count_appearance_column = [dict() for i in range(size)]
    count_appearance_block = [dict() for i in range(size)]

    # Count appearance of numbers within rows, columns, and blocks
    for row in range(size):
        temp_list = list()

        # Iterate through the columns of a row and count appearance of numbers
        for col in range(size):
            if (row,col) in cache_values.keys():
                for value in cache_values[(row,col)]:
                    temp_list.append(value)
        temp_set = set(temp_list)
        for number in temp_set:
            count_appearance_row[row][number] = temp_list.count(number)


    for col in range(size):
        temp_list = list()

        # Iterate through the rows of a column and count appearance of numbers
        for row in range(size):
            if (row,col) in cache_values.keys():
                for value in cache_values[(row,col)]:
                    temp_list.append(value)
        temp_set = set(temp_list)
        for number in temp_set:
            count_appearance_column[col][number] = temp_list.count(number)

    # Iterate through the different blocks of the board and count appearance of numbers
    row_block_start = 0
    col_block_start = 0
    block_no = 0
    while True:
        row_block_end = row_block_start + subgrid_size
        col_block_end = col_block_start + subgrid_size
        temp_list = list()
        for row in range(row_block_start, row_block_end):
            for col in range(col_block_start, col_block_end):
                if (row,col) in cache_values.keys():
                    for value in cache_values[(row,col)]:
                        temp_list.append(value)
        temp_set = set(temp_list)
        for number in temp_set:
            count_appearance_block[block_no][number] = temp_list.count(number)
        if row_block_start == (size-subgrid_size) and col_block_start == (size-subgrid_size):
            break
        elif col_block_start == (size-subgrid_size):
            row_block_start += subgrid_size
            col_block_start = 0
        else:
            col_block_start += subgrid_size
        block_no += 1

    # Assign priority to cache values based on appearance frequency
    for row in range(size):
        for col in range(size):
            temp_list = list()
            block_no = (row // subgrid_size) * subgrid_size + col // subgrid_size
            if (row,col) in cache_values.keys():
                for value in cache_values[(row,col)]:
                    freq = count_appearance_row[row][value] + count_appearance_column[col][value] + count_appearance_block[block_no][value]
                    temp_list.append(freq)
                cache_priority[(row,col)] = temp_list

    # Sort cache values based on their appearance frequency
    for row in range(size):
        for col in range(size):
            if (row,col) in cache_values.keys():
                cache_values[(row,col)] = [i for _,i in sorted(zip(cache_priority[(row,col)], cache_values[(row,col)]))]
    
    # Set board values where a legitimate value appears only once for either rows, columns, or blocks
    values_found = False
    for row in range(size):
        for col in range(size):
            temp_list = list()
            block_no = (row // subgrid_size) * subgrid_size + col // subgrid_size
            if (row,col) in cache_values.keys():
                for value in cache_values[(row,col)]:
                    if count_appearance_row[row][value] == 1 or count_appearance_column[col][value] == 1 or count_appearance_block[block_no][value] == 1:
                        board[row][col] = value
                        values_found = True
                        break                   
    return values_found, cache_values


# execution block
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("---> Usage : python script.py <input_file.txt>")
        print("** place the input text files inside inputs folder Eg: inputs/input1.txt **")
        sys.exit(1)
    
    file_name = sys.argv[1]
    file_path = f"inputs/{file_name}"
    board, size = read_board(file_path)

    values_found = True
    while values_found:
        valid_cache = find_valid_cache_values(board, size)
        values_found, ordered_cache = order_valid_cache_values(board, valid_cache, size)

    start_time = time.time()
    if solve(board, ordered_cache, size):
        end_time = time.time()
        out_file = write_output_to_file(board, file_path)
        print(f"\n\n%%%%%%% YOUR SUDOKU IS SOLVED! A copy is saved in '{out_file}' %%%%%%%", end="\n\n")
        print_board(board)
    else:
        end_time = time.time()
        print("No Solution")

    time_taken = end_time - start_time
    print(f"Time taken to solve: {time_taken} s   |   {(time_taken * 1000):.4f} ms")