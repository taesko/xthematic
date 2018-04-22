import functools

import collections
import contextlib
import json
import re
import subprocess

import xredit.colors
import xredit.config


def loaded_colors():
    queried = subprocess.Popen(['xrdb', '-query'], stdout=subprocess.PIPE)
    grepped = subprocess.check_output(['grep', 'color'], stdin=queried.stdout)
    queried.wait()
    lines = grepped.splitlines()
    matches = (re.match(pattern=b'.*color(\d+):\t([^ ]+)', string=l) for l in lines)
    grouped = (m.groups() for m in matches)
    cast = ((int(num), byte_arr.decode(encoding='ascii')) for num, byte_arr in grouped)
    colors = {}
    for number, hex_code in sorted(cast):
        if number in colors and hex_code != colors[number]:
            raise RuntimeError(f"color{number} has more than one value")
        cid = xredit.colors.ColorIdentifier(number)
        c = xredit.colors.Color(hex_code)
        colors[cid] = c
    return colors  # values are sorted by keys


def read_customized_colors():
    with xredit.config.USER_CUSTOM_FILE.open() as f:
        json_dict = json.load(f)
    color_strings = json_dict.get(xredit.config.TERMINAL_SESSION_ID, {})
    colors = {}
    for index, hex_code in color_strings.items():
        index = int(index)
        colors[xredit.colors.ColorIdentifier(index)] = xredit.colors.Color(hex_code)
    return colors


def save_custom_color(color_id, color):
    with xredit.config.USER_CUSTOM_FILE.open(mode='r') as f:
        json_dict = json.load(f)
    color_hexes = json_dict.get(xredit.config.TERMINAL_SESSION_ID, {})
    color_hexes[str(color_id.id)] = str(color.hex)
    json_dict[xredit.config.TERMINAL_SESSION_ID] = color_hexes
    with xredit.config.USER_CUSTOM_FILE.open(mode='w') as f:
        json.dump(obj=json_dict, fp=f)


def remove_custom_color(color_id):
    with xredit.config.USER_CUSTOM_FILE.open(mode='r') as f:
        json_dict = json.load(f)
    color_hexes = json_dict.get(xredit.config.TERMINAL_SESSION_ID, {})
    color = color_hexes[str(color_id.id)]
    del color_hexes[str(color_id.id)]
    json_dict[xredit.config.TERMINAL_SESSION_ID] = color_hexes
    with xredit.config.USER_CUSTOM_FILE.open(mode='w') as f:
        json.dump(obj=json_dict, fp=f)


def reset_custom_colors():
    with xredit.config.USER_CUSTOM_FILE.open(mode='r') as f:
        json_dict = json.load(f)
    if xredit.config.TERMINAL_SESSION_ID in json_dict:
        del json_dict[xredit.config.TERMINAL_SESSION_ID]
    with xredit.config.USER_CUSTOM_FILE.open(mode='w') as f:
        json.dump(obj=json_dict, fp=f)


class _TermColors(collections.MutableMapping):
    """ Interface to terminal colors."""

    def __init__(self):
        # TODO include defaults for missing customized colors
        # TODO make this object a constantly updating view/model
        self.loaded = loaded_colors()
        # TODO make this object a constantly updating view/model of the json file
        self.custom = read_customized_colors()
        self.colors = DictView(self.loaded, self.custom)

    def __iter__(self):
        yield from self.colors

    def __len__(self):
        return len(self.colors)

    def __getitem__(self, color_id):
        return self.colors[color_id]

    def __setitem__(self, color_id, color):
        if self.colors[color_id] == color:
            print(color_id, 'is already set')
            return

        index = str(color_id.id)
        r, g, b = map(str, color.rgb_large_percentage)
        initc = subprocess.run(['tput', 'initc', index, r, g, b])
        initc.check_returncode()
        if self.loaded[color_id] == color and color_id in self.custom:
            print('deleting custom color', self.custom[color_id])
            remove_custom_color(color_id)
            del self.custom[color_id]
        elif self.loaded[color_id] == color:
            assert False, f'{color} is not a custom color, but previously {color_id} was overwrited in loaded'
        else:
            self.custom[color_id] = color
            save_custom_color(color_id, color)

    def __delitem__(self, color_id):
        raise NotImplementedError()

    @contextlib.contextmanager
    def tryout(self, color_id, color):
        """ Swap the hex code of a color_id for the open terminal with a new one during the context."""
        old_color = self[color_id]
        self[color_id] = color
        yield
        self[color_id] = old_color

    def __repr__(self):
        return "{self.__class__}({colors})".format(
            self=self, colors=repr(self.colors)[1:-1]
        )


class DictView(collections.Mapping):

    def __init__(self, *dictionaries):
        self.dictionaries = dictionaries
        dct_keys = (dct.keys() for dct in self.dictionaries)
        self.all_keys = functools.reduce(lambda a, b: a.union(b), dct_keys, set())

    def __len__(self):
        return len(self.all_keys)

    def __iter__(self):
        yield from self.all_keys

    def __getitem__(self, item):
        for dct in reversed(self.dictionaries):
            if item in dct:
                return dct[item]
        else:
            raise KeyError(f'key {item} not found.')


TERMINAL_COLORS = _TermColors()
