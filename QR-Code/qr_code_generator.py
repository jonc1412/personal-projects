# Create a QR-code using matplotlib
import numpy as np
import matplotlib.pyplot as plt
import reedsolo

# Format strip tells reader how to read the QR-code
# 4 Different types of error correction
# L is the most basic type
# Specifies the mask type (8 types)
# For future, the mask needs to be done and check which of the mask performs the best
# Uses the best performing mask
# Mask performance is based on how little clusters of black and white there are 
def generate_format_strip(error_level, mask):
    error_dict = {'L' : '01', 'M' : '00', 'Q' : '11', 'H' : '10'}
    poly_string = '10100110111'
    error_string = error_dict[error_level]
    mask_string = '{:03b}'.format(mask)
    error_mask_string = error_string + mask_string + '0'*10
    error_mask_string = bin(int(error_mask_string, 2))[2:]

    while len(error_mask_string) > 10:
        while len(poly_string) != len(error_mask_string):
            poly_string += '0'
        error_mask_string = bin(int(error_mask_string, 2) ^ int(poly_string, 2))[2:]
        poly_string = '10100110111'


    while len(error_mask_string) < 10:
        error_mask_string = '0' + error_mask_string

    # Print statements to check for correct error_mask_string
    # Issue with left-most zeros not being added
    # print(f'Error String: {error_string}')
    # print(f'Mask String: {mask_string}')
    # print(f'error_mask_string: {error_mask_string}')

    final_string = bin(int(error_string + mask_string + error_mask_string, 2) ^ 0b101010000010010)[2:]
    return final_string

def generate_reed_solomon(data, ecc_count):
    rs = reedsolo.RSCodec(ecc_count)
    full_block = rs.encode(bytes(data))
    ecc_words = full_block[-ecc_count:]
    return list(ecc_words)

# Generates the data bits for the QR-code
# The first 4 bits specify the type of data that will be used in the QR-code
# Uses binary encoding
# The next 8 bits specifies the length of the data string
# Each 8 bit block corresponds to 1 character of the string
# Pad each of the data so that it becomes exactly 8 bits in total
# Reed-solomon error correction to fill in the rest of the QR-code
# Hard-coded to use error correction 7
def generate_qr_data(data, total_bytes, ecc_count):
    length = len(data) + 2
    data_binary = '0100' + '{:08b}'.format(len(data)) + ''.join(f'{ord(c):08b}' for c in data)
    pad_bytes = [0xEC, 0x11]
    pad_index = 0

    print(f'Data length (non-binary): {length}')

    # check each elem of the list to see if it's 8-bit aligned
    test_list = []
    for each in data:
        each = bin(ord(each))[2:]
        while len(each) < 8:
            each = '0' + each
        test_list.append(each)
    print(test_list)
    print(data_binary[12:])

    while length < total_bytes:
        data_binary += '{:08b}'.format(pad_bytes[pad_index % 2])
        pad_index += 1
        length += 1
    
    data_binary += '0000'
    data_list = []
    for i in range(0, length * 8, 8):
        data_list.append(int(data_binary[i:i+8], 2))

    ecc_words = generate_reed_solomon(data_list, ecc_count)

    for each in ecc_words:
        data_binary += '{:08b}'.format(each)

    return data_binary

generate_qr_data("wikipedia", 19, 7)

def create_qr_code(data):
    # Size of the QR-Code 
    grid_size = 21
    matrix = np.zeros((grid_size, grid_size), dtype=int)
    check_matrix = np.zeros((grid_size, grid_size), dtype=int)

    # Binary representation of data
    binary_data_string = generate_qr_data(data, 19, 7)

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
                if counter < len(binary_data_string) and check_matrix[row][col] != 1:
                    matrix[row][col] = int(binary_data_string[counter])
                    counter += 1
                if counter < len(binary_data_string) and check_matrix[row][col-1] != 1:
                    matrix[row][col-1] = int(binary_data_string[counter])
                    counter += 1
                row -= 1
            row += 1
        else:
            while row < grid_size:
                if counter < len(binary_data_string) and check_matrix[row][col] != 1:
                    matrix[row][col] = int(binary_data_string[counter])
                    counter += 1
                if counter < len(binary_data_string) and check_matrix[row][col-1] != 1:
                    matrix[row][col-1] = int(binary_data_string[counter])
                    counter += 1
                row += 1
            row -= 1

        if col == 8:
            col -= 3
        else:
            col -= 2
            
    # Format Strip (Error Correction)
    level = 'L'  # Error Correction Level L
    mask = 6  # Mask Pattern 0
    format_strip = generate_format_strip(level, mask)

    for i in range(7):
        if i < 6:
            matrix[8][i] = format_strip[i]
        else:
            matrix[8][i+1] = format_strip[i]
        matrix[grid_size-i-1][8] = format_strip[i]
    
    for i in range(8):
        if i < 6:
            matrix[i][8] = format_strip[i+7]
        else:
            matrix[i+1][8] = format_strip[i+7]
        matrix[8][grid_size-i-1] = format_strip[i+7]

    for row in range(rows):
        for col in range(cols):
            if check_matrix[row][col] != 1:
                if (((row*col)%2) + ((row*col)%3))%2==0:
                    matrix[row][col] ^= 1

    plt.imshow(matrix, cmap="binary", interpolation="nearest")
    plt.axis("off")
    plt.show()

    print(matrix)
    print("\n")
    print(check_matrix)

# print(create_qr_code('www.wikipedia.org'))