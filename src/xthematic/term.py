import functools
import json
import logging
import re
import subprocess

import collections

import xthematic.colors
import xthematic.config

logger = logging.getLogger(__name__)


def keep_updated(method):
    @functools.wraps(method)
    def new_method(self, *args, **kwargs):
        if self.is_outdated():
            self.update()
        return method(self, *args, **kwargs)

    return new_method


class _LoadedColors(collections.Mapping):

    def __init__(self):
        self._colors = {}
        self._hash = ''
        logger.debug('initialized %s instance %s', self.__class__.__name__, self)

    @staticmethod
    def xrdb_hash():
        return hash(subprocess.check_output(['xrdb', '-query']))

    @staticmethod
    def loaded():
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
            cid = xthematic.colors.ColorIdentifier(number)
            c = xthematic.colors.Color(hex_code)
            colors[cid] = c
        return colors  # values are sorted by keys

    @keep_updated
    def __iter__(self):
        yield from self._colors

    @keep_updated
    def __len__(self):
        return len(self._colors)

    @keep_updated
    def __getitem__(self, k):
        return self._colors[k]

    def update(self):
        # print(self)
        # logger.info('updating _LoadedColors instance %s', self)
        self._colors = self.loaded()
        self._hash = self.xrdb_hash()
        # logger.info('loaded color identifiers: %s', [c.id for c in self._colors])

    def is_outdated(self):
        return self._hash != self.xrdb_hash()


LOADED_COLORS = _LoadedColors()


class _CustomColors(collections.MutableMapping):
    def __init__(self, session_id=xthematic.config.TERMINAL_SESSION_ID):
        self._session_id = session_id
        self._colors = self.read_customized_colors(self._session_id)
        logger.debug('initialized %s instance %s', self.__class__.__name__, self)
        logging.info('custom colors are %s', self._colors)

    @staticmethod
    def custom_dict():
        with xthematic.config.USER_CUSTOM_FILE.open() as f:
            return json.load(f)

    @staticmethod
    def read_customized_colors(session_id=xthematic.config.TERMINAL_SESSION_ID):
        json_dict = _CustomColors.custom_dict()
        color_strings = json_dict.get(session_id, {})
        colors = {}
        for index, hex_code in color_strings.items():
            index = int(index)
            colors[xthematic.colors.ColorIdentifier(index)] = xthematic.colors.Color(hex_code)
        return colors

    def __len__(self) -> int:
        return len(self._colors)

    def __iter__(self):
        yield from self._colors

    def __getitem__(self, item):
        return self._colors[item]

    def __setitem__(self, color_id, color):
        json_dict = self.__class__.custom_dict()
        color_hexes = json_dict.get(self._session_id, {})
        color_hexes[str(color_id.id)] = str(color.hex)
        json_dict[xthematic.config.TERMINAL_SESSION_ID] = color_hexes
        with xthematic.config.USER_CUSTOM_FILE.open(mode='w') as f:
            json.dump(obj=json_dict, fp=f)
        self._colors[color_id] = color
        logger.info('set custom color %s to %s', color_id, color)

    def __delitem__(self, color_id):
        json_dict = self.__class__.custom_dict()
        color_hexes = json_dict.get(self._session_id, {})
        color = color_hexes[str(color_id.id)]
        assert color == self._colors[color_id].hex
        del color_hexes[str(color_id.id)]
        json_dict[xthematic.config.TERMINAL_SESSION_ID] = color_hexes
        with xthematic.config.USER_CUSTOM_FILE.open(mode='w') as f:
            json.dump(obj=json_dict, fp=f)
        logger.info('removed custom color %s with hex %s', color_id, color)
        del self._colors[color_id]

    def reset(self):
        json_dict = self.__class__.custom_dict()
        if self._session_id in json_dict:
            del json_dict[self._session_id]
        with xthematic.config.USER_CUSTOM_FILE.open(mode='w') as f:
            json.dump(obj=json_dict, fp=f)
        logger.info('reset all custom colors')
        logger.info('removed colors: ', self._colors)
        self._colors.clear()


CUSTOM_COLORS = _CustomColors()


class _TermColors(collections.MutableMapping):
    """ Interface to terminal colors."""

    def __init__(self):
        # TODO include defaults for missing customized colors
        self.loaded = LOADED_COLORS
        self.custom = CUSTOM_COLORS
        self.colors = DictView(self.loaded, self.custom)

    def __iter__(self):
        yield from self.colors

    def __len__(self):
        return len(self.colors)

    def __getitem__(self, color_id):
        return self.colors[color_id]

    def __setitem__(self, color_id, color):
        if self.colors[color_id] == color:
            logger.debug('%s is already set to %s', color_id, color)
            return

        index = str(color_id.id)
        r, g, b = map(str, color.rgb_large_percentage)
        initc = subprocess.run(['tput', 'initc', index, r, g, b])
        initc.check_returncode()
        logger.info('set terminal color %s to %s', color_id, color)
        if self.loaded[color_id] == color and color_id in self.custom:
            del self.custom[color_id]
        elif self.loaded[color_id] == color:
            msg = f'{color} is not a custom color, but previously {color_id} was overwrited in loaded'
            logger.critical(msg)
            assert False, msg
        else:
            self.custom[color_id] = color

    def __delitem__(self, color_id):
        raise NotImplementedError()

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