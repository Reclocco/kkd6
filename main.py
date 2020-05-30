import copy
import math
import sys


def check():
    f1 = open('ex.tga', "rb")
    f2 = open('out.tga', "rb")

    f1.read(12)
    f1.read(2)
    f1.read(2)
    f1.read(2)

    f2.read(12)
    x = f2.read(2)
    y = f2.read(2)
    f2.read(2)

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

    for i in range(x * y):
        b_byte1 = int.from_bytes(f1.read(1), byteorder='little')
        g_byte1 = int.from_bytes(f1.read(1), byteorder='little')
        r_byte1 = int.from_bytes(f1.read(1), byteorder='little')

        b_byte2 = int.from_bytes(f2.read(1), byteorder='little')
        g_byte2 = int.from_bytes(f2.read(1), byteorder='little')
        r_byte2 = int.from_bytes(f2.read(1), byteorder='little')

        quadra_b += math.pow((b_byte1 - b_byte2), 2)
        quadra_g += math.pow((g_byte1 - g_byte2), 2)
        quadra_r += math.pow((r_byte1 - r_byte2), 2)
        quadra_all += math.pow((b_byte1 - b_byte2), 2) + \
                      math.pow((g_byte1 - g_byte2), 2) + \
                      math.pow((r_byte1 - r_byte2), 2)

        sum_b += b_byte2 ** 2
        sum_g += g_byte2 ** 2
        sum_r += r_byte2 ** 2
        sum_all += b_byte2 ** 2 + g_byte2 ** 2 + r_byte2 ** 2

    mse = [quadra_b / (x * y), quadra_g / (x * y), quadra_r / (x * y)]

    snr = []
    try:
        snr.append(sum_b / (x * y) / (quadra_b / (x * y)))
    except ZeroDivisionError:
        snr.append(float("inf"))

    try:
        snr.append(sum_g / (x * y) / (quadra_g / (x * y)))
    except ZeroDivisionError:
        snr.append(float("inf"))

    try:
        snr.append(sum_r / (x * y) / (quadra_r / (x * y)))
    except ZeroDivisionError:
        snr.append(float("inf"))

    print("mse r:", mse[2])
    print("mse g:", mse[1])
    print("mse b:", mse[0])
    print("mse all:", sum(mse))

    print("snr r:", snr[0])
    print("snr g:", snr[1])
    print("snr b:", snr[2])
    print("snr all:", sum(snr))


def decode():
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

    bottom_encoded = []
    top_encoded = []

    for i in range(int(x * y / 2)):
        top_pixel = [int.from_bytes(encoded.read(1), byteorder='little'),
                     int.from_bytes(encoded.read(1), byteorder='little'),
                     int.from_bytes(encoded.read(1), byteorder='little')]
        top_encoded.append([top_pixel[k] - 128 for k in range(3)])

        bottom_sign = [int.from_bytes(encoded.read(1), byteorder='little'),
                       int.from_bytes(encoded.read(1), byteorder='little'),
                       int.from_bytes(encoded.read(1), byteorder='little')]

        bottom_pixel = [int.from_bytes(encoded.read(1), byteorder='little'),
                        int.from_bytes(encoded.read(1), byteorder='little'),
                        int.from_bytes(encoded.read(1), byteorder='little')]

        for k in range(3):
            if bottom_sign[k] == 0:
                bottom_pixel[k] = -bottom_pixel[k]

        if i == 0:
            bottom_encoded.append(bottom_pixel)
        else:
            bottom_encoded.append([bottom_pixel[k] + bottom_encoded[i - 1][k] for k in range(3)])

    for i in range(int(x * y / 2)):
        if i != 0:
            for k in range(3):
                try:
                    out.write((int(bottom_encoded[i][k] - top_encoded[i][k])).to_bytes(1, 'little'))
                except OverflowError:
                    if int(bottom_encoded[i][k] - top_encoded[i][k]) < 0:
                        out.write((0).to_bytes(1, 'little'))
                    else:
                        out.write((255).to_bytes(1, 'little'))

            for k in range(3):
                try:
                    out.write((int(bottom_encoded[i][k] + top_encoded[i][k])).to_bytes(1, 'little'))
                except OverflowError:
                    if int(bottom_encoded[i][k] + top_encoded[i][k]) < 0:
                        out.write((0).to_bytes(1, 'little'))
                    else:
                        out.write((255).to_bytes(1, 'little'))

        else:
            for k in range(3):
                try:
                    out.write((int(bottom_encoded[i][k] + top_encoded[i][k])).to_bytes(1, 'little'))
                except OverflowError:
                    if int(bottom_encoded[i][k] + top_encoded[i][k]) < 0:
                        out.write((0).to_bytes(1, 'little'))
                    else:
                        out.write((255).to_bytes(1, 'little'))

    for k in range(3):
        try:
            out.write(
                (int(bottom_encoded[int(x * y / 2) - 1][k] + top_encoded[int(x * y / 2) - 1][k])).to_bytes(1, 'little'))
        except OverflowError:
            if int(bottom_encoded[int(x * y / 2) - 1][k] + top_encoded[int(x * y / 2) - 1][k]) < 0:
                out.write((0).to_bytes(1, 'little'))
            else:
                out.write((255).to_bytes(1, 'little'))

    out.write(encoded.read(26))


def encode(bits):
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
    top = []

    b_prev = 0
    g_prev = 0
    r_prev = 0

    diff = []

    idx = 0
    diff.append([0, 0, 0])

    for i in range(x * y):
        b_byte = int.from_bytes(f.read(1), byteorder='little')
        g_byte = int.from_bytes(f.read(1), byteorder='little')
        r_byte = int.from_bytes(f.read(1), byteorder='little')

        if i != 0:
            top.append([(b_byte - b_prev) / 2, (g_byte - g_prev) / 2, (r_byte - r_prev) / 2])
            bottom.append([(b_byte + b_prev) / 2, (g_byte + g_prev) / 2, (r_byte + r_prev) / 2])
        else:
            top.append([b_byte, g_byte, r_byte])
            bottom.append(copy.deepcopy([0, 0, 0]))

        if i % 2 == 0:
            for k in range(3):
                encoded.write((belong(sectors, top[i][k] + 128)).to_bytes(1, 'little'))

            try:
                diff.append([bottom[i][k] - bottom[i - 2][k] -
                             math.floor(diff[idx - 1][k]) + diff[idx - 1][k] for k in range(3)])

                for k in range(3):
                    if diff[idx][k] < 0:
                        encoded.write((0).to_bytes(1, 'little'))
                    else:
                        encoded.write((1).to_bytes(1, 'little'))

                for k in range(3):
                    try:
                        encoded.write(
                            (int(math.fabs(math.floor(diff[idx][k])))).to_bytes(1, 'little'))

                    except OverflowError:
                        print(bottom[i], bottom[i - 2], [bottom[i][k] - bottom[i - 2][k] for k in range(3)], diff[idx])
                        sys.exit(0)

            except IndexError:
                for k in range(3):
                    encoded.write((1).to_bytes(1, 'little'))

                for k in range(3):
                    encoded.write((int(bottom[i][k])).to_bytes(1, 'little'))

            idx += 1

        b_prev = copy.deepcopy(b_byte)
        g_prev = copy.deepcopy(g_byte)
        r_prev = copy.deepcopy(r_byte)

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
    encode(1)
    decode()
    check()


main()
