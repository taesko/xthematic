import contextlib

import click
import sty

import xthematic.colors
import xthematic.themes
from xthematic.term import TERMINAL_COLORS


class ColoredContext:
    all_color_identifiers = set(xthematic.colors.ColorIdentifier.all_four_bit_colors())

    def __init__(self):
        self.overwritten_colors = {}

    @property
    def registered_ids(self):
        return set(self.overwritten_colors.keys())

    @property
    def unregistered_ids(self):
        return self.all_color_identifiers - self.registered_ids

    def register_color(self, color):
        if len(self.unregistered_ids) < 0:
            raise RuntimeError("cannot register any more color values.")
        elif color in xthematic.term.TERMINAL_COLORS.values():
            raise ValueError(f"color {color} is already defined in the terminal's colors")

        id_ = self.unregistered_ids.pop()
        self.overwritten_colors[id_] = xthematic.term.TERMINAL_COLORS[id_]
        xthematic.term.TERMINAL_COLORS[id_] = color

    def unregister_color(self, color):
        id_ = self.id_for_color(color)
        xthematic.term.TERMINAL_COLORS[id_] = self.overwritten_colors[id_]
        del self.overwritten_colors[id_]

    def unregister_all(self):
        for id_ in self.registered_ids:
            xthematic.term.TERMINAL_COLORS[id_] = self.overwritten_colors[id_]
        self.overwritten_colors.clear()

    def format_string_for(self, fg=None, bg=None):
        s = '{}' + sty.rs.all
        if fg:
            id_ = self.id_for_color(fg)
            s = sty.fg(id_.four_bit_color_name) + s
        if bg:
            id_ = self.id_for_color(bg)
            s = sty.bg(id_.four_bit_color_name) + s
        return s

    @staticmethod
    def printable_colors():
        return xthematic.term.TERMINAL_COLORS.values()

    @staticmethod
    def id_for_color(color):
        for id_, value in xthematic.term.TERMINAL_COLORS.items():
            if value == color:
                return id_
        raise ValueError(f"there is no registered {color}")


class ColoredStream:
    def __init__(self, context):
        self.context = context

    @classmethod
    @contextlib.contextmanager
    def open(cls):
        cc = ColoredContext()
        yield cls(context=cc)
        cc.unregister_all()

    def echo(self, text, nl=True, fg=None, bg=None):
        if fg and fg not in self.context.printable_colors():
            self.context.register_color(fg)
        if bg and bg not in self.context.printable_colors():
            self.context.register_color(bg)
        s = self.context.format_string_for(fg=fg, bg=bg)
        click.echo(s.format(text), nl=nl)


def escape_sequence_index_string(fg_id, bg_id):
    fg_bright = int(fg_id.id in range(8, 16))
    return f'{fg_bright};{30+(fg_id.id % 8)};{40+(bg_id.id % 8)}'


def echo_theme(theme_name=None):
    if theme_name:
        colors = xthematic.themes.theme_colors(theme_name)
    else:
        colors = xthematic.term.TERMINAL_COLORS
    with ColoredStream.open() as stream:
        for row_id in xthematic.colors.ColorIdentifier.all_four_bit_colors():
            stream.echo(text=row_id, fg=colors[row_id], nl=True)
            # for col_id in list(xthematic.colors.ColorIdentifier.all_four_bit_colors())[:8]:
            #     stream.echo(text=escape_sequence_index_string(fg_id=row_id, bg_id=col_id),
            #                 nl=False, fg=colors[row_id], bg=colors[col_id])
            #     click.echo(' ', nl=False)
            # click.echo(nl=True)
        input()


