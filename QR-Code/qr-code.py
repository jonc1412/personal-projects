# Create a QR-code using matplotlib
import numpy as np
import matplotlib.pyplot as plt

def create_qr_code(data):
    # Binary representation of data
    binary_data = ''
    grid_size = 21
    matrix = np.zeros((grid_size, grid_size), dtype=int)

    for char in data:
        binary_data += '{0:08b}'.format(ord(char))

    print(matrix)




data = "hello"
create_qr_code(data)