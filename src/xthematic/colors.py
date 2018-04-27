""" Color conversion."""


class Color:
    """ Color formats."""
    alpha_num = "100"

    def __init__(self, hex_code):
        if not self.is_valid_hex_code(hex_code):
            raise ValueError("{} is not a valid hex code".format(hex_code))
        self._hex = hex_code

    @staticmethod
    def is_valid_hex_code(value):
        if value.startswith('#'):
            nums = value[1:]
        else:
            nums = value
        if len(nums) != 6:
            return False
        try:
            int(nums, base=16)
        except ValueError:
            return False
        return True

    @property
    def hex(self):
        return self._hex

    @property
    def rgb(self):
        if self.hex.startswith('#'):
            hex_code = self.hex[1:]
        else:
            hex_code = self.hex
        colors = []
        hex_code = iter(hex_code)
        for a in hex_code:
            b = next(hex_code)
            ci = int(a+b, base=16)
            colors.append(ci)
        return tuple(colors)

    @property
    def rgb_percentage(self):
        return self.rgb_percented(accuracy=100)

    @property
    def rgb_large_percentage(self):
        # there is a proper word for this...
        return self.rgb_percented(accuracy=1000)

    def rgb_percented(self, accuracy=100):
        perc = []
        for part in self.rgb:
            p = (part / 256) * accuracy
            perc.append(int(p))
        return perc

    def __hash__(self):
        return hash(self._hex)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._hex == other._hex

    def __repr__(self):
        return f"{self.__class__.__name__}({self._hex})"


class ColorIdentifier:
    """ Color identifier formats."""

    all_four_bit_color_names = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    all_four_bit_color_names = all_four_bit_color_names + ['li_' + c for c in all_four_bit_color_names]

    def __init__(self, id):
        if not self.__class__.is_valid(color_id=id):
            raise ValueError(f'color_id {id!r} is not valid')
        self._id = id

    @classmethod
    def is_valid(cls, color_id):
        return color_id in range(0, 16)

    @classmethod
    def all_four_bit_colors(cls):
        yield from map(cls, range(0, 16))

    @classmethod
    def all_resources(cls):
        for k in range(0, 16):
            yield cls(k)

    @property
    def resource_id(self):
        return 'color' + str(self.id)

    @property
    def id(self):
        return self._id

    @property
    def escape_sequence_index(self):
        if self.id in range(8):
            return str(30 + self.id)
        elif self.id in range(8, 16):
            return f'1;{40 + self.id - 8}'
        else:
            return None

    @property
    def four_bit_color_name(self):
        return self.all_four_bit_color_names[self.id]

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id!r})"
