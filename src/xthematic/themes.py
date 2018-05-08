import itertools
import os
import subprocess

import xrp
import xrp.parser

import xthematic.colors
import xthematic.config
import xthematic.term

AUTO_GENERATED_TEMPLATE = (
    "! auto generated colors from xthematic\n"
    "!\n"
    "!\n"
    "{}\n"
    "! xthematic end\n"
)


class ThemeContents:
    def __init__(self, colormap, *, _text=None):
        if _text:
            assert colormap == self.colors_of_string(_text)
        else:
            _text = self.string_from_colors(colormap)

        self._text = _text
        self.colormap = colormap

    @classmethod
    def from_name(cls, name):
        return cls.from_file(xthematic.config.USER_THEME_DIR / name)

    @classmethod
    def from_file(cls, file):
        return cls.from_string(_read_text(file))

    @classmethod
    def from_string(cls, string):
        dct = cls.colors_of_string(string)
        return cls(colormap=dct, _text=string)

    @staticmethod
    def colors_of_string(string):
        parsed = xrp.parse(string)
        dct = {}
        for color_id in xthematic.colors.ColorIdentifier.all_resources():
            try:
                hex_code = parsed.resources['*' + color_id.resource_id]
                dct[color_id] = xthematic.colors.Color(hex_code)
            except KeyError:
                pass
        return dct

    @staticmethod
    def string_from_colors(colormap):
        return ''.join(itertools.starmap(resource_string, colormap.items()))

    @property
    def colors(self):
        return self.colormap

    @property
    def text(self):
        return self._text


def save_terminal_colors(theme_name, overwrite=False):
    theme_file = xthematic.config.USER_THEME_DIR / theme_name
    if theme_file.exists() and not overwrite:
        raise FileExistsError(r'there already exists a theme {theme_name!r}')
    string = AUTO_GENERATED_TEMPLATE.format(ThemeContents.string_from_colors(xthematic.term.TERMINAL_COLORS))
    try:
        _write_text(theme_file, string)
    except Exception:
        if theme_file.exists():
            os.remove(theme_file)
        raise


def activate_theme(name, permanent=True, link_file=None):
    """
    :param name: name of the theme file in xthematic.config.USER_THEME_DIR
    :param permanent: boolean flag whether the resources should be loaded and
    the theme included in the ~/.Xresources file
    :param link_file: a link_file to configure pointing to the theme file. Does not modify
    the ~/.Xresources file if parameter is present.
    :return: None
    """
    terminal_theme = ThemeContents(xthematic.term.TERMINAL_COLORS)
    activate_theme_in_terminal(name)
    if permanent:
        if link_file:
            tmp = backup_file_path(file_path=link_file)
            os.symlink(xthematic.config.USER_THEME_DIR / name, tmp)
            os.rename(src=tmp, dst=link_file)
            subprocess.check_call(['xrdb', '-load', xthematic.config.USER_XRESOURCES_FILE])
        else:
            include_theme_in_resources(name, xthematic.config.USER_XRESOURCES_FILE)
            include = '-I' + str(xthematic.config.USER_THEME_DIR)
            subprocess.check_call(['xrdb', include, '-load', xthematic.config.USER_XRESOURCES_FILE])
        _write_text(xthematic.config.USER_OLD_THEME_FILE, '')  # truncate
    else:
        _write_text(xthematic.config.USER_OLD_THEME_FILE, terminal_theme.text)


def deactivate_theme():
    """ Deactivate a temporary theme."""
    for color_id, color in old_theme_colors().items():
        xthematic.term.TERMINAL_COLORS[color_id] = color

    _write_text(xthematic.config.USER_OLD_THEME_FILE, '')  # truncate


def remove_theme(name):
    t = xthematic.config.USER_THEME_DIR / name
    if t.exists():
        os.remove(t)
    else:
        raise FileNotFoundError("can't remove a theme that doesn't exist.")


def include_theme_in_resources(name, resource_file):
    """ Includes a theme in a resource file using an include statement.

    A backup of the original resource file is left in the directory with a '.backup' suffix
    """
    theme_file = xthematic.config.USER_THEME_DIR / name
    if not theme_file.is_file():
        raise FileNotFoundError("theme file doesn't exist")
    incl_string = str(xrp.parser.XIncludeStatement(include_file=name))
    output_file = backup_file_path(resource_file, suffix='.out')
    with open(resource_file, mode='r', encoding='utf-8') as input_:
        with open(output_file, mode='w', encoding='utf-8') as out:
            for line in replace_auto_generated(stream=input_, new_value=incl_string):
                out.write(line)
    os.rename(resource_file, backup_file_path(resource_file, can_exist=True))
    os.rename(output_file, resource_file)


def activate_theme_in_terminal(name):
    for color_id, color in theme_colors(theme_name=name).items():
        # TODO activating a theme sets all of the themes colors as custom - perhaps rethink activation
        xthematic.term.TERMINAL_COLORS[color_id] = color


def all_themes():
    return os.listdir(xthematic.config.USER_THEME_DIR)


def theme_colors(theme_name):
    return ThemeContents.from_name(theme_name).colors


def old_theme_colors():
    return ThemeContents.from_file(xthematic.config.USER_OLD_THEME_FILE).colors


def resource_string(color_id, color, nl=True):
    s = f"*{color_id.resource_id}: {color.hex}"
    return s + '\n' if nl else s


def replace_auto_generated(stream, new_value):
    # filter the autogenerated template
    for filtered in filter_auto_generated(stream):
        yield filtered
    new_lines = AUTO_GENERATED_TEMPLATE.format(new_value)
    for line in new_lines:
        yield line


def filter_auto_generated(stream):
    stream = iter(stream)
    current_template_line = 0
    template_lines = AUTO_GENERATED_TEMPLATE.splitlines(keepends=True)
    # filter template start
    for line in stream:
        if line == template_lines[current_template_line]:
            if current_template_line == 2:
                break
            else:
                current_template_line += 1
        else:
            yield line
    # filter old value and template end
    for line in stream:
        if line == template_lines[-1]:
            break

    for leftover in stream:
        yield leftover


def backup_file_path(file_path, suffix='.backup', can_exist=False):
    """ Return file_path with a suffix that is guaranteed to be unique inside it's directory.

    If can_exists is True uniqueness won't be guaranteed.
    """
    if can_exist:
        return file_path.with_suffix(suffix)

    sid = str(hash(str(file_path)))
    for k in range(len(sid)):
        file_backup = file_path.with_suffix(suffix + sid[:k])
        if not file_backup.exists():
            return file_backup
    else:
        raise RuntimeError("wtf")


def _write_text(file, text):
    """ Write to file in utf-8 encoding."""
    with open(file, mode='w', encoding='utf-8') as f:
        return f.write(text)


def _read_text(file):
    """ Read a file in utf-8 encoding."""
    with open(file, mode='r', encoding='utf-8') as f:
        return f.read()
