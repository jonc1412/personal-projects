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
    
    for i in range(8, grid_size-8):
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
    
    # Error correction 
    while len(total_data) % 8 != 0:
        total_data += '0'

    rs = reedsolo.RSCodec(7)
    byte_length = (len(total_data) + 7) // 8
    data_bytes = int(total_data, 2).to_bytes(byte_length, 'big')    
    error_correction_bytes = rs.encode(data_bytes)[-7:]
    error_correction_binary = ''.join(f'{byte:08b}' for byte in error_correction_bytes)
    full_binary_data = total_data + error_correction_binary

    leftover_data = '1110110000010001'

    # Arranging bytes on the grid
    # Follows a zig-zag pattern that snakes itself to the top right
    rows, cols = grid_size, grid_size
    counter = 0
    leftover_counter = 0
    row = rows - 1
    col = cols - 1
    
    while col > -1:
        if row == grid_size - 1:
            while row >= 0:
                if counter < len(full_binary_data) and check_matrix[row][col] != 1:
                    matrix[row][col] = int(full_binary_data[counter])
                    counter += 1
                elif counter >= len(full_binary_data) and check_matrix[row][col] != 1:
                    matrix[row][col] = int(leftover_data[leftover_counter%16])
                    leftover_counter += 1

                if counter < len(full_binary_data) and check_matrix[row][col-1] != 1:
                    matrix[row][col-1] = int(full_binary_data[counter])
                    counter += 1
                elif counter >= len(full_binary_data) and check_matrix[row][col-1] != 1:
                    matrix[row][col-1] = int(leftover_data[leftover_counter%16])
                    leftover_counter += 1
                row -= 1
            row += 1
        else:
            while row < grid_size:
                if counter < len(full_binary_data) and check_matrix[row][col] != 1:
                    matrix[row][col] = int(full_binary_data[counter])
                    counter += 1
                elif counter >= len(full_binary_data) and check_matrix[row][col] != 1:
                    matrix[row][col] = int(leftover_data[leftover_counter%16])
                    leftover_counter += 1
                    
                if counter < len(full_binary_data) and check_matrix[row][col-1] != 1:
                    matrix[row][col-1] = int(full_binary_data[counter])
                    counter += 1
                elif counter >= len(full_binary_data) and check_matrix[row][col-1] != 1:
                    matrix[row][col-1] = int(leftover_data[leftover_counter%16])
                    leftover_counter += 1
                row += 1
            row -= 1

        if col == 8:
            col -= 3
        else:
            col -= 2
        
    print(matrix)
    
    # Format Strip (Error Correction)
    # Convert binary strings to integers for polynomial operations
    level = '01'  # Error Correction Level L
    mask = '000'  # Mask Pattern 0
    full_error = int(level + mask, 2)
    generator = 0b10100110111
    data = full_error << 10
    for shift in range(14, 9, -1):
        if (data & (1 << shift)) != 0:
            data ^= (generator << (shift - 10))
    remainder = data & 0x3FF
    format_15_bits_str = '{:05b}{:010b}'.format(full_error, remainder)
    mask_str = '101010000010010'
    mask_int = int(mask_str, 2)
    final_format_int = int(format_15_bits_str, 2) ^ mask_int
    final_format_string = f"{final_format_int:015b}"

    for i in range(7):
        if i < 6:
            matrix[8][i] = final_format_string[i]
        else:
            matrix[8][i+1] = final_format_string[i]
        matrix[grid_size-i-1][8] = final_format_string[i]
    
    for i in range(8):
        if i < 6:
            matrix[i][8] = final_format_string[i+7]
        else:
            matrix[i+1][8] = final_format_string[i+7]
        matrix[8][grid_size-i-1] = final_format_string[i+7]

    for row in range(rows):
        for col in range(cols):
            if check_matrix[row][col] != 1:
                if (row + col) % 2 == 0:
                    matrix[row][col] ^= 1
    
    
    plt.imshow(matrix, cmap="binary", interpolation="nearest")
    plt.axis("off")
    plt.show()

data = "www.twitch.tv"
create_qr_code(data)