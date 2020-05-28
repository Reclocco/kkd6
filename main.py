import copy
import math
import sys

image = []


def read_tga(bits):
    global image
    sectors = [int(math.pow(2, 8 - bits) / 2 + i * math.pow(2, 8 - bits)) for i in range(int(math.pow(2, bits)))]

    f = open('ex.tga', "rb")
    out = open('out.tga', "wb")
    out.write(f.read(12))

    x = f.read(2)
    out.write(x)

    y = f.read(2)
    out.write(y)

    out.write(f.read(2))

    x = int.from_bytes(x, byteorder='little')
    y = int.from_bytes(y, byteorder='little')

    quadra_all = 0
    quadra_b = 0
    quadra_g = 0
    quadra_r = 0
    sum_b = 0
    sum_g = 0
    sum_r = 0
    sum_all = 0

    diff_code = []
    bottom = []
    top = []
    b_prev = 0
    g_prev = 0
    r_prev = 0
    b_byte = 0
    g_byte = 0
    r_byte = 0
    for i in range(x * y):
        b_byte = int.from_bytes(f.read(1), byteorder='little')
        g_byte = int.from_bytes(f.read(1), byteorder='little')
        r_byte = int.from_bytes(f.read(1), byteorder='little')

        bottom.append([(b_byte + b_prev) / 2, (g_byte + g_prev) / 2, (r_byte + r_prev) / 2])
        top.append([(b_byte - b_prev) / 2, (g_byte - g_prev) / 2, (r_byte - r_prev) / 2])
        image.append([b_byte, g_byte, r_byte])

        b_prev = copy.deepcopy(b_byte)
        g_prev = copy.deepcopy(g_byte)
        r_prev = copy.deepcopy(r_byte)

    for i in range(int(x * y / 2)):
        for k in range(3):
            try:
                out.write((belong(sectors, int(bottom[2*i][k] - top[2*i][k])).to_bytes(1, 'little')))
            except OverflowError:
                out.write((0).to_bytes(1, 'little'))

        for k in range(3):
            try:
                out.write((int(bottom[2*i][k] + top[2*i][k])).to_bytes(1, 'little'))
            except OverflowError:
                out.write((255).to_bytes(1, 'little'))

    out.write(f.read(26))


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


main()
