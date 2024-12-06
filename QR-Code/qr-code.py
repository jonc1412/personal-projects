# Create a QR-code using matplotlib
import numpy as np
import matplotlib.pyplot as plt
import reedsolo

def create_qr_code(data):
    # Size of the QR-Code 
    grid_size = 21
    matrix = np.zeros((grid_size, grid_size), dtype=int)
    check_matrix = np.zeros((grid_size, grid_size), dtype=int)

    # Binary representation of data
    binary_data = ''
    for char in data:
        binary_data += '{0:08b}'.format(ord(char))
    binary_data += '0000'

    data_type = str(format(4, '04b'))
    char_length = str(format(len(data), '08b'))

    total_data = data_type + char_length + binary_data

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

    for i in range(8):
        for j in range(8):
            check_matrix[i][j] = 1
            check_matrix[grid_size-i-1][j] = 1
            check_matrix[i][grid_size-j-1] = 1

    # Timing Pattern: Helps align the QR code grid
    # Alternating black and white cells, starting with black
    # Horizontal Pattern: Row = 6 and Columns = 8 to (grid_size-9)
    # Vertical Pattern: Column = 6 and Rows = 8 to (grid_size-9)
    for i in range(8, grid_size-8, 2):
        matrix[6][i] = 1
        matrix[i][6] = 1
        check_matrix[6][i] = 1
        check_matrix[i][6] = 1

    # Alignment Pattern: (only necessary with version 2 and above)

    # Format Strips: Contain rules for how to scan the code
    # For now, fill them with 2s

    # Top-Left Format Strip
    for i in range(9):
        for j in range(9):
            if i == 8 or j == 8:
                if matrix[i][j] != 1:
                    matrix[i][j] = 2
                    check_matrix[i][j] = 1

    # Top-Right Format Strip
    for i in range(8):
        matrix[8][grid_size-i-1] = 2
        check_matrix[8][grid_size-i-1] = 1

    # Bottom-Left Format Strip
    for i in range(7):
        matrix[grid_size-i-1][8] = 2
        check_matrix[grid_size-i-1][8] = 1
    
    # 1 special pixel (no specific reason) is 1 in the Format Strip
    matrix[grid_size-8][8] = 1
    check_matrix[grid_size-8][8] = 1

    # Start to encode the data (Zig-zag pattern) starting bottom right
    # Type of data
    # First 4: 0001 (Numeric), 0010 (Alphanumeric), 0100 (Binary), 1000 (Japanese Kanji)
    index = 0
    for i in range(2):
        for j in range(2):
            matrix[grid_size-i-1][grid_size-j-1] = data_type[index]
            check_matrix[grid_size-i-1][grid_size-j-1] = 1
            index += 1

    # Number of characters in the message
    index = 0
    for i in range(2, 6):
        for j in range(2):
            matrix[grid_size-i-1][grid_size-j-1] = char_length[index]
            check_matrix[grid_size-i-1][grid_size-j-1] = 1
            index += 1
    
    # Error correction 
    while len(total_data) % 8 != 0:
        total_data += '0'

    rs = reedsolo.RSCodec(7)
    data_bytes = int(total_data, 2).to_bytes(len(total_data))
    error_correction_bytes = rs.encode(data_bytes)[-7:]
    error_correction_binary = ''.join(f'{byte:08b}' for byte in error_correction_bytes)
    full_binary_data = total_data + error_correction_binary

    left_over_data = '1110110000010001'

    # Arranging bytes on the grid
    # Follows a zig-zag pattern that snakes itself to the top right
    rows, cols = grid_size, grid_size
    counter = 0
    left_over_counter = 0
    row = rows - 1
    for col in range(cols - 1, -1, -2):
        if row == grid_size - 1:
            while row >= 0:
                if check_matrix[row][col] != 1:
                    if counter < len(full_binary_data):
                        matrix[row][col] = int(full_binary_data[counter])
                        counter += 1
                    else:
                        matrix[row][col] = int(left_over_data[left_over_counter % 16])
                        left_over_counter += 1
                if check_matrix[row][col-1] != 1:
                    if counter < len(full_binary_data):
                        matrix[row][col-1] = int(full_binary_data[counter])
                        counter += 1   
                    else:
                        matrix[row][col-1] = int(left_over_data[left_over_counter % 16]) 
                        left_over_counter += 1
                row -= 1
            row += 1
        else:
            while row < grid_size:
                if check_matrix[row][col] != 1:
                    if counter < len(full_binary_data):
                        matrix[row][col] = int(full_binary_data[counter])
                        counter += 1
                    else:
                        matrix[row][col] = int(left_over_data[left_over_counter % 16])
                        left_over_counter += 1
                if check_matrix[row][col-1] != 1:
                    if counter < len(full_binary_data):
                        matrix[row][col-1] = int(full_binary_data[counter])
                        counter += 1   
                    else:
                        matrix[row][col-1] = int(left_over_data[left_over_counter % 16]) 
                        left_over_counter += 1
                row += 1
            row -= 1
        
    # Format Strip (Error Correction)
    # Convert binary strings to integers for polynomial operations
    def compute_bch(data, generator):
        data = int(data, 2)
        generator = int(generator, 2)

        data <<= 10

        for i in range(len(bin(data)) - len(bin(generator)), -1, -1):
            if data & (1 << (i + len(bin(generator)) - 3)):
                data ^= generator << i

        return f'{data:010b}'

    # Example Input
    level = '01'  # Error Correction Level L
    mask = '000'  # Mask Pattern 0
    full_error = mask + level  # First 5 bits of the format string
    generator = '10100110111'  # BCH Generator Polynomial

    # Compute BCH Remainder
    remainder = compute_bch(full_error, generator)

    # Combine to get the full 15-bit format string
    format_string = full_error + remainder

    # Top-Left Horizontal Format Strip
    for i in range(7):
        if i < 6:
            matrix[8][i] = format_string[i]
        else:
            matrix[8][i+1] = format_string[i]
        matrix[grid_size-i-1][8] = format_string[i]

    
    for i in range(8):
        if i < 6:
            matrix[i][8] = format_string[i+7]
        else:
            matrix[i+1][8] = format_string[i+7]
        matrix[8][grid_size-i-1] = format_string[i+7]


data = "www.twitch.com"
create_qr_code(data)