from qr_code_generator import *
import qrcode
import matplotlib.pyplot as plt

# Example QR-code using python's qrcode library
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)


# plt.imshow(img, cmap="gray")
# plt.axis("off")
# plt.show()

# Testing generate_format_string function
# Ecc Level: L 
# Mask Pattern: 0
# Result should be: 111011111000100
assert(generate_format_strip('L', 0) == '111011111000100')
assert(generate_format_strip('L', 1) == '111001011110011')
assert(generate_format_strip('L', 2) == '111110110101010')
assert(generate_format_strip('L', 3) == '111100010011101')

# Testing generate_reed_soloman function
# assert(generate_reed_solomon())

# Testing QR-code generator
# create_qr_code('www.wikipedia.com')