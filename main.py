import copy
import math
import sys


def read_encoded():
    encoded = open('encoded.tga', "rb")
    out = open('out.tga', 'wb')
    out.write(encoded.read(12))

    x = encoded.read(2)
    out.write(x)

    y = encoded.read(2)
    out.write(y)

    out.write(encoded.read(2))

    x = int.from_bytes(x, byteorder='little')
    y = int.from_bytes(y, byteorder='little')
    print(x, y)

    prev = [0, 0, 0]
    for i in range(x * y):
        pixel = [int.from_bytes(encoded.read(1), byteorder='little'),
                 int.from_bytes(encoded.read(1), byteorder='little'),
                 int.from_bytes(encoded.read(1), byteorder='little')]

        if i % 2 == 1:
            print(pixel)
            prev = [(prev[k] + pixel[k] - 170) for k in range(3)]
            print(prev)
            for k in range(3):
                out.write((prev[k]).to_bytes(1, 'little'))
        else:
            for k in range(3):
                out.write((pixel[k]).to_bytes(1, 'little'))

    out.write(encoded.read(26))


def read_tga(bits):
    sectors = [int(math.pow(2, 8 - bits) / 2 + i * math.pow(2, 8 - bits)) for i in range(int(math.pow(2, bits)))]

    f = open('ex.tga', "rb")
    encoded = open('encoded.tga', "wb")
    encoded.write(f.read(12))

    x = f.read(2)
    encoded.write(x)

    y = f.read(2)
    encoded.write(y)

    encoded.write(f.read(2))

    x = int.from_bytes(x, byteorder='little')
    y = int.from_bytes(y, byteorder='little')

    bottom = []
    bottom_encoded = []
    top = []
    top_encoded = []

    b_prev = 0
    g_prev = 0
    r_prev = 0

    image = []
    for i in range(x * y):
        b_byte = int.from_bytes(f.read(1), byteorder='little')
        g_byte = int.from_bytes(f.read(1), byteorder='little')
        r_byte = int.from_bytes(f.read(1), byteorder='little')

        image.append(b_byte)
        image.append(g_byte)
        image.append(r_byte)

        top.append([(b_byte - b_prev) / 2, (g_byte - g_prev) / 2, (r_byte - r_prev) / 2])
        bottom.append([(b_byte + b_prev) / 2, (g_byte + g_prev) / 2, (r_byte + r_prev) / 2])

        top_encoded.append([belong(sectors, top[i][k] + 128) - 128 for k in range(3)])

        # try:
        #     diff = [bottom[i][k] - bottom[i - 1][k] + 128 for k in range(3)]
        #
        #     bottom_encoded.append(diff)
        # except IndexError:
        #     bottom_encoded.append(bottom[i])

        b_prev = copy.deepcopy(b_byte)
        g_prev = copy.deepcopy(g_byte)
        r_prev = copy.deepcopy(r_byte)

    for i in range(int(x * y / 2)):
        if i != 0:
            for k in range(3):
                try:
                    encoded.write((int(bottom[2 * i][k] - top_encoded[2 * i][k])).to_bytes(1, 'little'))
                except OverflowError:
                    if int(bottom[2 * i][k] - top_encoded[2 * i][k]) < 0:
                        encoded.write((0).to_bytes(1, 'little'))
                    else:
                        encoded.write((255).to_bytes(1, 'little'))

            for k in range(3):
                try:
                    encoded.write((int(bottom[2 * i][k] + top_encoded[2 * i][k])).to_bytes(1, 'little'))
                except OverflowError:
                    if int(bottom[2 * i][k] + top_encoded[2 * i][k]) < 0:
                        encoded.write((0).to_bytes(1, 'little'))
                    else:
                        encoded.write((255).to_bytes(1, 'little'))

        else:
            for k in range(3):
                try:
                    encoded.write((int(bottom[2 * i][k] + top_encoded[2 * i][k])).to_bytes(1, 'little'))
                except OverflowError:
                    if int(bottom[2 * i][k] + top_encoded[2 * i][k]) < 0:
                        encoded.write((0).to_bytes(1, 'little'))
                    else:
                        encoded.write((255).to_bytes(1, 'little'))

    for k in range(3):
        encoded.write((int(bottom[x * y - 1][k] + top_encoded[x * y - 1][k])).to_bytes(1, 'little'))

    encoded.write(f.read(26))


def belong(sectors, x):
    inc = sectors[0] * 2
    s_size = inc

    if inc == 0:
        inc = 1
        s_size = 0

    i = 0
    while x > s_size:
        s_size += inc
        i += 1

    return sectors[math.floor(i)]


def main():
    read_tga(3)
    # read_encoded()


main()
