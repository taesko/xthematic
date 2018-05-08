import logging
import os
import pathlib

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.WARNING)
CONSOLE_HANDLER.setFormatter(logging.Formatter(fmt='{levelname}: {message}', style='{'))
root_logger.addHandler(CONSOLE_HANDLER)


def file_state_ok(file, default_text=''):
    if file.exists():
        if not os.access(file, mode=os.R_OK | os.W_OK):
            logging.warning("can't r/w to file %s", file)
        return True

    try:
        file.write_text(default_text)
    except OSError:
        logging.warning("file '%s' doesn't exist and couldn't be created", file)
        return False

    return True


def get_safe_file(file, backup=None, default_text=''):
    """ Get a safe file path that is guaranteed to exist and have r/w access.

    Returns the file argument if file_state_ok is true for it.
    Returns the backup argument if it's supplied and file_state_ok is not true for the first argument.
    Otherwise raises RuntimeError
    """
    if file_state_ok(file, default_text=default_text):
        return file
    elif backup and file_state_ok(backup):
        logging.info("can't r/w to file %s, using backup %s", file, backup)
        return backup
    else:
        if backup:
            raise RuntimeError("can't r/w to file %s", file)
        else:
            raise RuntimeError("can't r/w to file %s or backup %s", file, backup)


def get_safe_dir(path):
    if not path.exists():
        path.mkdir(exist_ok=True)
    return path


def get_multiple(dct, keys, default=None):
    for key in keys:
        if key in dct:
            return dct[key]
    else:
        if not default:
            raise KeyError("dct doesn't contain any of keys")
        else:
            return default


def user_config_home():
    try:
        return get_multiple(os.environ, 'XDG_CONFIG_HOME')
    except KeyError:
        return pathlib.Path(os.environ['HOME'], '.config')


try:
    TERMINAL_SESSION_ID = os.environ['TERM_SESSION_ID']
except KeyError:
    logging.critical('$TERM_SESSION_ID variable is not set - see install instructions.')
    raise

USER_CONFIG_DIR = get_safe_dir(user_config_home() / 'xthematic')
USER_THEME_DIR = get_safe_dir(pathlib.Path(os.environ.get('XTHEMES_DIR', USER_CONFIG_DIR / 'themes')))
USER_CONFIG_FILE = get_safe_file(USER_CONFIG_DIR / 'config')
USER_CUSTOM_FILE = get_safe_file(USER_CONFIG_DIR / 'custom', default_text='{}')
USER_OLD_THEME_FILE = get_safe_file(USER_CONFIG_DIR / 'old_theme')
USER_XRESOURCES_FILE = get_safe_file(pathlib.Path(os.environ['HOME'], '.Xresources'))

LOG_FILE = get_safe_file(pathlib.Path('/var/log/xthematic.log'),
                         backup=pathlib.Path(USER_CONFIG_DIR / 'logs'))

LOG_FILE_HANDLER = logging.FileHandler(str(LOG_FILE))
LOG_FILE_HANDLER.setLevel(logging.DEBUG)
fmt_s = '{asctime} ' + TERMINAL_SESSION_ID[-4:] + ' {module}.{funcName} line {lineno}: {levelname}: {message}'
LOG_FILE_HANDLER.setFormatter(logging.Formatter(fmt=fmt_s, style='{'))
root_logger.addHandler(LOG_FILE_HANDLER)

_xlf = os.environ.get('XTHEME_LINK_FILE', None)
USER_THEME_LINK_FILE = pathlib.Path(_xlf) if _xlf else _xlf
