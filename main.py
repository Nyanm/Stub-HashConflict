import random
from matplotlib import pyplot as plt
import numpy as np
import hashlib

big = 2 ** 96 - 1
small = 2 ** 32 - 1

sample_s = 1000000
sample_b = 10 * sample_s
err_size = 10

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


def process(hash_method, get_data, size: int) -> np.array:
    data_set = []
    hashed = np.zeros(hashed_size, dtype=np.uint8)

    for index in range(size):
        data_set.append(get_data(hash_method))

    err_len = err_size
    err = np.zeros(err_len, dtype=np.uint32)
    for data in data_set:
        if hashed[data]:
            err[hashed[data] + 1] += 1
            err[hashed[data]] -= 1
        hashed[data] += 1

    return err


def dual_process(hash_method_1, hash_method_2, size: int):
    data_set_1, data_set_2 = [], []
    hashed_1 = np.zeros(hashed_size, dtype=np.uint8)
    hashed_2 = np.zeros(hashed_size, dtype=np.uint8)

    for index in range(size):
        raw = random.randint(0, big)
        press_1_1 = hash_method_1(raw, 96)
        press_1_2 = hash_method_1(press_1_1, 48)
        data_set_1.append(press_1_2)
        press_2_1 = hash_method_2(raw, 96)
        press_2_2 = hash_method_2(press_2_1, 48)
        data_set_2.append(press_2_2)

    err = np.zeros((err_size, err_size), dtype=int)
    for index in range(size):
        if hashed_1[data_set_1[index]] and hashed_2[data_set_2[index]]:
            err[hashed_1[data_set_1[index]] + 1][hashed_2[data_set_2[index]] + 1] += 1
            err[hashed_1[data_set_1[index]]][hashed_2[data_set_2[index]]] -= 1
        hashed_1[data_set_1[index]] += 1
        hashed_2[data_set_2[index]] += 1

    err = err[2:, 2:]

    return err


def conflict_test():
    uni_s = process(hash_method=xor_hash, get_data=get_uni, size=sample_s)
    sep_s = process(hash_method=xor_hash, get_data=get_sep, size=sample_s)
    uni_b = process(hash_method=xor_hash, get_data=get_uni, size=sample_b)
    sep_b = process(hash_method=xor_hash, get_data=get_sep, size=sample_b)

    msg = '|Name     |Sample    |2 times  |3 times  |4 times  ' \
          '|5 times  |6 times  |7 times  |8 times  |9 times  |10 times'
    m_1 = ' UniSmall  1000000   '
    m_2 = ' SepSmall  1000000   '
    m_3 = ' UniBig    10000000  '
    m_4 = ' SepBig    10000000  '

    for index in range(2, 11):
        m_1 += ' %-9s' % uni_s[index]
        m_2 += ' %-9s' % sep_s[index]
        m_3 += ' %-9s' % uni_b[index]
        m_4 += ' %-9s' % sep_b[index]

    print(msg, m_1, m_2, m_3, m_4, sep='\n')

    """
    |Name     |Sample    |2 times  |3 times  |4 times  |5 times  |6 times  |7 times  |8 times  |9 times  |10 times
     UniSmall  1000000    27850     575       12        0         0         0         0         0         0        
     SepSmall  1000000    27869     557       12        0         0         0         0         0         0        
     UniBig    10000000   1642449   327159    48417     5753      592       56        7         0         0        
     SepBig    10000000   1643721   326907    48684     5890      560       48        4         0         0        
    """


if __name__ == '__main__':
    print(dual_process(xor_hash, sum_hash, sample_b))
