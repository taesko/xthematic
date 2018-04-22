import os
import pathlib


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


USER_CONFIG_DIR = user_config_home() / 'xredit'
USER_CONFIG_FILE = USER_CONFIG_DIR / 'config'
USER_CUSTOM_FILE = USER_CONFIG_DIR / 'custom'
USER_XRESOURCES_FILE = pathlib.Path(os.environ['HOME'], '.Xresources')
USER_THEME_DIR = pathlib.Path(os.environ.get('XTHEMES_DIR', USER_CONFIG_DIR / 'themes'))

USER_CONFIG_DIR.mkdir(exist_ok=True)
USER_THEME_DIR.mkdir(exist_ok=True)
if not USER_CONFIG_FILE.exists():
    USER_CONFIG_FILE.write_text('')
if not USER_CUSTOM_FILE.exists():
    USER_CUSTOM_FILE.write_text('{}', encoding='ascii')  # write an empty json object so the file is decodable

LOG_FILE = pathlib.Path('/var/log/xredit.log')
BACKUP_LOG_FILE = pathlib.Path(USER_CONFIG_DIR / 'logs')
BACKUP_LOG_FILE.write_text('')
if not LOG_FILE.exists():
    print(f"log file {LOG_FILE} doesn't exist")
    if os.access(LOG_FILE, os.R_OK | os.W_OK):
        LOG_FILE.write_text('')
    else:
        print("can't create log file - no r/w permissions")
        LOG_FILE = BACKUP_LOG_FILE
        print(f"using backup log file {LOG_FILE}")

TERMINAL_SESSION_ID = os.environ['TERM_SESSION_ID']
_xlf = os.environ.get('XTHEME_LINK_FILE', None)
USER_THEME_LINK_FILE = pathlib.Path(_xlf) if _xlf else _xlf
