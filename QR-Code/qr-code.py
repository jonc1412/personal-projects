# Create a QR-code using matplotlib
import numpy as np
import matplotlib.pyplot as plt

def create_qr_code(data):
    # Size of the QR-Code 
    grid_size = 21
    matrix = np.zeros((grid_size, grid_size), dtype=int)
    filled_matrix = np.zeros((grid_size, grid_size), dtype=int)

    # Binary representation of data
    binary_data = ''
    for char in data:
        binary_data += '{0:08b}'.format(ord(char))

    data_type = str(format(4, '04b'))
    char_length = str(format(len(data), '08b'))

    # Finder Pattern
    # No matter the size of the grid_size, always 7x7
    # Orientation: 
    # Outer-border is filled
    # 1 ring of white space (Quiet zone)
    # Rest filled

    # Top-Left Finder Pattern
    for i in range(7):
        for j in range(7):
            if i in {0, 6} or j in {0, 6}:
                matrix[i][j] = 1
            if 2 <= i <= 4 and 2 <= j <= 4:
                matrix[i][j] = 1

    # Top-Right Finder Pattern
    for i in range(0, 7):
        for j in range(grid_size-7, grid_size):
            if i in {0, 6} or j in {grid_size-7, grid_size-1}:
                matrix[i][j] = 1
            if 2 <= i <= 4 and grid_size-5 <= j <= grid_size-3:
                matrix[i][j] = 1

    # Bottom-Left Finder Pattern
    for i in range(grid_size-7, grid_size):
        for j in range(0, 7):
            if i in {grid_size-7, grid_size-1} or j in {0, 6}:
                matrix[i][j] = 1
            if grid_size-5 <= i <= grid_size-3 and 2 <= j <= 4:
                matrix[i][j] = 1

    # Timing Pattern: Helps align the QR code grid
    # Alternating black and white cells, starting with black
    # Horizontal Pattern: Row = 6 and Columns = 8 to (grid_size-9)
    # Vertical Pattern: Column = 6 and Rows = 8 to (grid_size-9)
    for i in range(8, grid_size-8, 2):
        matrix[5][i] = 1
        matrix[i][5] = 1

    # Alignment Pattern: (only necessary with version 2 and above)

    # Format Strips: Contain rules for how to scan the code
    # For now, fill them with 2s

    # Top-Left Format Strip
    for i in range(9):
        for j in range(9):
            if i == 8 or j == 8:
                if matrix[i][j] != 1:
                    matrix[i][j] = 2

    # Top-Right Format Strip
    for i in range(8):
        matrix[8][grid_size-i-1] = 2

    # Bottom-Left Format Strip
    for i in range(7):
        matrix[grid_size-i-1][8] = 2
    
    # 1 special pixel (no specific reason) is 1 in the Format Strip
    matrix[grid_size-8][8] = 1

    # Start to encode the data (Zig-zag pattern) starting bottom right
    # Type of data
    # First 4: 0001 (Numeric), 0010 (Alphanumeric), 0100 (Binary), 1000 (Japanese Kanji)
    index = 0
    for i in range(2):
        for j in range(2):
            matrix[grid_size-i-1][grid_size-j-1] = data_type[index]
            index += 1

    # Number of characters in the message
    index = 0
    for i in range(2, 6):
        for j in range(2):
            matrix[grid_size-i-1][grid_size-j-1] = char_length[index]
            index += 1

    # Arranging bytes on the grid
    # Follows a zig-zag pattern that snakes itself to the top right
    m = np.zeros((grid_size, grid_size), dtype=int)
    rows, cols = grid_size, grid_size
    counter = 0
    row = rows - 1
    for col in range(cols - 1, -1, -2):
        if row == grid_size - 1:
            while row >= 0:
                if counter < len(binary_data):
                    m[row][col] = binary_data[counter]
                    counter += 1
                if counter < len(binary_data):
                    m[row][col-1] = binary_data[counter]
                    counter += 1    
                row -= 1
            row += 1
        else:
            while row < grid_size:
                if counter < len(binary_data):
                    m[row][col] = binary_data[counter]
                    counter += 1
                if counter < len(binary_data):
                    m[row][col-1] = binary_data[counter]
                    counter += 1    
                row += 1
            row -= 1

data = "www.twitch.com"
create_qr_code(data)