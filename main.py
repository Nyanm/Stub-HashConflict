import random
from matplotlib import pyplot as plt
import numpy as np
import hashlib

big = 2 ** 96 - 1
small = 2 ** 32 - 1

sample_s = 1000000
sample_b = 10 * sample_s

hashed_size = 2 ** 24
shake = hashlib.shake_128()


def xor_hash(num: int, bits: int) -> int:
    high = num >> (bits // 2)
    low = num % (2 ** (bits // 2))
    xor = high ^ low
    return xor


def sum_hash(num: int, bits: int) -> int:
    high = num >> (bits // 2)
    low = num % (2 ** (bits // 2))
    add = (high + low) % (2 ** (bits // 2))
    return add


def shake_hash(num: int, bits: int) -> int:
    shake.update(str(num).encode('utf-8'))
    hex_str = shake.hexdigest(bits // 16)
    press = int('0x%s' % hex_str, 0)
    return press


def get_uni(hash_method) -> int:
    raw = random.randint(0, big)
    press_1 = hash_method(raw, 96)
    press_2 = hash_method(press_1, 48)
    return press_2


def get_sep(hash_method) -> int:
    press_1 = []
    for __index in range(3):
        raw = random.randint(0, small)
        __press_1 = hash_method(raw, 32)
        press_1.append(__press_1)
    press_1[0] = press_1[0] << 32
    press_1[1] = press_1[1] << 16
    press_1[2] = press_1[2]
    press_1 = sum(press_1)
    press_2 = hash_method(press_1, 48)
    return press_2


def process(hash_method, sep: bool = False) -> tuple:
    data_set = []
    hashed = np.zeros(hashed_size, dtype=np.uint8)
    if sep:
        get_data = get_sep
    else:
        get_data = get_uni

    for index in range(sample_s):
        data_set.append(get_data(hash_method))

    err_s = 0
    for data in data_set:
        if hashed[data]:
            err_s += 1
        hashed[data] += 1

    for index in range(sample_b - sample_s):
        data_set.append(get_data(hash_method))

    err_b = 0
    for data in data_set[sample_s:]:
        if hashed[data]:
            err_b += 1
        hashed[data] += 1

    return err_s, err_b


if __name__ == '__main__':
    
    xor_uni = process(xor_hash)
    print(xor_uni)
    add_uni = process(sum_hash)
    print(add_uni)
    sha_uni = process(shake_hash)
    print(sha_uni)

    xor_sep = process(xor_hash, True)
    print(xor_sep)
    add_sep = process(sum_hash, True)
    print(add_sep)
    sha_sep = process(shake_hash, True)
    print(sha_sep)

    uni_s, uni_b = [xor_uni[0], add_uni[0], sha_uni[0]], [xor_uni[1], add_uni[1], sha_uni[1]] 
    sep_s, sep_b = [xor_sep[0], add_sep[0], sha_sep[0]], [xor_sep[1], add_sep[1], sha_sep[1]] 
    
    fig = plt.figure(figsize=(8, 10))
    width = 0.25
    labels = ['XOR', 'ADD', 'Shake-128']
    x = np.arange(len(labels))

    def __plot(__uni, __sep, title):
        plt.ylim((0, int(1.3 * max(__uni + __sep))))
        uni_num = plt.bar(x - width / 2, __uni, width, label='Uni 96-Bit data')
        sep_num = plt.bar(x + width / 2, __sep, width, label='Sep 96-Bit data')
        plt.bar_label(uni_num, padding=3)
        plt.bar_label(sep_num, padding=3)
        plt.ylabel('Conflict')
        plt.title(title)
        plt.xticks(x, labels)
        plt.legend()

    plt.subplot(211)
    __plot(uni_s, sep_s, 'Sample size: 1,000,000')

    plt.subplot(212)
    __plot(uni_b, sep_b, 'Sample size: 1,000,000 + 9,000,000')

    plt.show()
