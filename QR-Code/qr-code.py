# Create a QR-code using matplotlib
import numpy as np
import matplotlib.pyplot as plt

def create_qr_code(data):
    binary_data = ''

    # Size of the QR-Code 
    grid_size = 21
    matrix = np.zeros((grid_size, grid_size), dtype=int)

    # Binary representation of data
    for char in data:
        binary_data += '{0:08b}'.format(ord(char))

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

# data = "Test"
# create_qr_code(data)