import random
from unittest import TestCase

import pytest

from xredit import colors


def byte_to_str(byte):
    if byte > 255:
        raise ValueError(f'{byte} is larger than a byte.')
    numerals = list(range(10)) + ['A', 'B', 'C', 'D', 'E', 'F']
    a = byte // 16
    b = byte % 16
    return f'{numerals[a]}{numerals[b]}'


def random_hex():
    t = [random.randrange(0, 256) for _ in range(3)]
    return ''.join(map(byte_to_str, t))


class TestColor:
    def test_is_valid_hex_code(self):
        assert colors.Color.is_valid_hex_code(random_hex())
        assert colors.Color.is_valid_hex_code('#' + random_hex())
        assert not colors.Color.is_valid_hex_code('?' + random_hex())
        assert not colors.Color.is_valid_hex_code(random_hex()[:-1])
        assert not colors.Color.is_valid_hex_code('#' + random_hex()[:-1])
        assert not colors.Color.is_valid_hex_code(random_hex() + '#')

    def test_hex(self):
        h = random_hex()
        assert colors.Color(h).hex == h
        assert colors.Color('#' + h).hex == '#' + h

    def test_rgb(self):
        hex_ = random_hex()
        for index, ele in enumerate(colors.Color(hex_).rgb):
            assert ele == int(hex_[index * 2: index * 2 + 2], base=16)

    def test_rgb_percentage(self):
        pass

    def test_rgb_large_percentage(self):
        pass

    def test_rgb_percented(self):
        pass


def random_four_bit_int():
    return random.randrange(0, 16)


class TestColorIdentifier(TestCase):

    def test_is_valid(self):
        assert colors.ColorIdentifier.is_valid(random_four_bit_int())

    def test_all_four_bit_colors(self):
        assert colors.ColorIdentifier(random_four_bit_int()) in colors.ColorIdentifier.all_four_bit_colors()

    def test_all_resources(self):
        pass

    def test_resource_id(self):
        index = random_four_bit_int()
        assert colors.ColorIdentifier(index).resource_id == 'color' + str(index)

    def test_id(self):
        index = random_four_bit_int()
        assert colors.ColorIdentifier(index).id == index

    def test_escape_sequence_index(self):
        for i in range(30, 38):
            assert colors.ColorIdentifier(i - 30).escape_sequence_index == str(i)
        for i in range(40, 48):
            assert colors.ColorIdentifier(i - 40 + 8).escape_sequence_index == f'1;{i}'

    def test_four_bit_color_name(self):
        names = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
        names = names + ['li_' + c for c in names]
        i = random_four_bit_int()
        assert colors.ColorIdentifier(i).four_bit_color_name == names[i]
