import functools
import string

import click
import collections

import xthematic.colors
import xthematic.config
import xthematic.display
import xthematic.term
import xthematic.themes


class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help_ = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help_ + (
                '\nNOTE: This argument is mutually exclusive with '
                f' arguments: [{ex_str}].'
            )
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                f"Illegal usage: `{self.name}` is mutually exclusive with "
                f"arguments `{self.mutually_exclusive}`."
            )

        return super().handle_parse_result(ctx, opts, args)


class DependentOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.dependencies = set(kwargs.pop('dependencies', []))
        help_ = kwargs.get('help', '')
        if self.dependencies:
            ex_str = ', '.join(self.dependencies)
            kwargs['help'] = help_ + (
                f' NOTE: This argument is dependent on arguments: [{ex_str}].'
            )
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.name in opts and not self.dependencies.issubset(opts):
            raise click.UsageError(
                f"Illegal usage: `{self.name}` depends on arguments `{self.dependencies}`."
            )

        return super().handle_parse_result(ctx, opts, args)


class ColorType(click.ParamType):
    name = "color"

    def convert(self, value, param, ctx):
        try:
            if not value.startswith('#'):
                return xthematic.colors.Color('#' + value)
            else:
                return xthematic.colors.Color(value)
        except ValueError:
            self.fail(f"{value!r} is not a valid hex code", param, ctx)


class ColorIdType(click.ParamType):
    name = 'ColorId'

    def convert(self, value, param, ctx):
        try:
            return xthematic.colors.ColorIdentifier(int(value))
        except (ValueError, TypeError):
            self.fail(f"{value!r} is not a valid color identifier")


class ColorViewType(click.ParamType):
    name = 'ColorView'
    ColorView = collections.namedtuple('ColorView', ['foreground', 'background', 'text'])

    def convert(self, value, param, ctx):
        parts = value.split(':')
        if len(parts) > 3:
            self.fail(f"{value!r} has too many fields")

        # all parts must be either a valid string or None
        _parts = []
        for p in parts:
            if p:
                _parts.append(p)
            else:
                _parts.append(None)
        parts = _parts
        parts.extend([None] * (3 - len(parts)))
        color_type = ColorType()
        convert = functools.partial(color_type.convert, param=param, ctx=ctx)
        for i in range(2):
            if parts[i]:
                parts[i] = convert(parts[i])
        return self.__class__.ColorView(*parts)


class XThemeType(click.ParamType):
    name = 'Xtheme'

    def convert(self, value, param, ctx):
        return value


@click.group()
def main():
    pass


@main.command()
@click.argument('color_views', type=ColorViewType(), nargs=-1, required=True)
@click.option('-f', '--foreground', type=ColorType(), help='default foreground')
@click.option('-b', '--background', type=ColorType(), help='default background')
@click.option('-t', '--text', type=str, default=string.ascii_letters, help='default text')
def view(color_views, foreground, background, text):
    """ display colors in the terminal through a color view spec.

    The command takes a variable number of color view arguments.
    A color view arg is defined as - 'foreground_hex:background_hex:text' and
    each of the elements can be omitted.
    Examples:
    '#FF0000::hello' specifies hello in red on the default background
    ':#FF0000' specifies default text with default color on a red background

    For each of the color views a line is printed with the corresponding foreground, background and text.

    The options '-f', '-b', '-t' can be used to specify default foreground, background and text
    otherwise the default for the terminal are used whilst text is all the ascii letters.
    """
    with xthematic.display.ColoredStream.open() as stream:
        nl = True
        for i, cv in enumerate(color_views):
            fg = cv.foreground or foreground
            bg = cv.background or background
            text = cv.text or text
            if i == len(color_views) - 1:
                nl = False
            stream.echo(text=text, fg=fg, bg=bg, nl=nl)
        input()  # wait for user to press Enter


def deactivate_theme(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    xthematic.themes.deactivate_theme()
    ctx.exit()


def list_themes(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(' '.join(xthematic.themes.all_themes()), nl=True)
    ctx.exit()


@main.command()
@click.argument('theme_name', type=XThemeType(), required=False)
@click.option('-d', '--deactivate', is_flag=True, default=False,
              is_eager=True, callback=deactivate_theme, expose_value=False,
              help="deactivate the current theme and return to terminal default colors")
@click.option('-l', '--list', is_flag=True, default=False,
              is_eager=True, callback=list_themes, expose_value=False,
              help="list all saved themes")
@click.option('-r', '--remove', is_flag=True, default=False,
              help="delete the specified theme")
@click.option('-a', '--activate', is_flag=True, default=False,
              cls=MutuallyExclusiveOption, mutually_exclusive=['save'],
              help="activate the theme in the terminal used to run the process")
@click.option('-p', '--permanent', is_flag=True, default=False,
              cls=DependentOption, dependencies=['activate'],
              help=("a supplementary option to --activate that will include the theme in "
                    "the user's ~/.Xresources file. Alternatively if the $XTHEME_LINK_FILE "
                    "environment variable is set will link the symlink to the theme file "
                    "and will not do any modifications to ~/.Xresources."))
@click.option('-s', '--save', is_flag=True, default=False,
              cls=MutuallyExclusiveOption, mutually_exclusive=['activate'],
              help="save the current terminal colors in a theme file.")
@click.option('-o', '--overwrite', is_flag=True, default=False,
              cls=DependentOption, dependencies=['save'],
              help="overwrite a theme file if it exists with the current terminal colors")
def theme(theme_name, remove, activate, permanent, save, overwrite):
    """ view, activate or save themes.

    The first argument to this command is a theme name (valid or invalid), if no theme_name
    is specified the current terminal colors are printed.

    Specifying a theme name without any options will print the themes colors
    to the terminal.

    The '--activate' and '--permanent' options are used for activating themes.
    While the '--save' and '--overwrite' options for saving.
    """
    if not theme_name:
        xthematic.display.echo_theme()
    elif activate:
        if xthematic.config.USER_THEME_LINK_FILE:
            xthematic.themes.activate_theme(theme_name, permanent=permanent,
                                            link_file=xthematic.config.USER_THEME_LINK_FILE)
        else:
            xthematic.themes.activate_theme(theme_name, permanent=permanent)
    elif save:
        xthematic.themes.save_terminal_colors(theme_name, overwrite=overwrite)
    elif remove:
        xthematic.themes.remove_theme(name=theme_name)
    else:
        xthematic.display.echo_theme(theme_name)


def reset_colors(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    xthematic.term.TERMINAL_COLORS.reset_customized()
    ctx.exit()


@main.command()
@click.argument('color_id', type=ColorIdType())
@click.argument('color', type=ColorType(), required=False)
@click.option('-r', '--reset', is_flag=True, default=False,
              is_eager=True, callback=reset_colors, expose_value=False,
              help="reset the customized colors for this session")
@click.option('-x', '--xresources', 'xresources_file', help='set or view inside this resources file',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
              cls=MutuallyExclusiveOption, mutually_exclusive=['theme_name', 'all_terminals'])
@click.option('-t', '--theme-name', help='set or view inside theme',
              type=XThemeType(),
              cls=MutuallyExclusiveOption, mutually_exclusive=['xresources_file', 'all_terminals'])
@click.option('-a', '--all-terminals', help='set or view the color in all open terminals',
              is_flag=True, default=False,
              cls=MutuallyExclusiveOption, mutually_exclusive=['theme_name', 'xresources_file'])
def color(color_id, color, xresources_file, theme_name, all_terminals):
    """ set or view color indexes for the current terminal.

    The command takes two arguments - a color id and a hex color code, the latter of which is optional.
    If hex color code is not specified it displays the currently loaded terminal color for that id.
    Otherwise it sets the terminal color for that id to the hex code.
    """
    def display_color(color_):
        with xthematic.display.ColoredStream.open() as stream:
            stream.echo(text=color_.hex, fg=color_, nl=True)
            stream.echo(text=color_.hex, bg=color_, nl=False)
            input()
        return

    if xresources_file:
        # TODO
        raise NotImplementedError()
    elif theme_name:
        # TODO
        if color:
            raise NotImplementedError()
        else:
            display_color(xthematic.themes.theme_colors(theme_name)[color_id])

    elif all_terminals:
        # TODO
        raise NotImplementedError()
    else:
        if color:
            xthematic.term.TERMINAL_COLORS[color_id] = color
        else:
            display_color(xthematic.term.TERMINAL_COLORS[color_id])


def edit():
    raise NotImplementedError()
