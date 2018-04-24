import logging

from xredit.config import LOG_FILE


LOG_FILE_HANDLER = logging.FileHandler(str(LOG_FILE))
LOG_FILE_HANDLER.setLevel(logging.DEBUG)
LOG_FILE_FORMATTER = logging.Formatter(fmt='{asctime} {module}.{funcname} line {lineno}: {levelname}: {message}',
                                       style='{')
LOG_FILE_HANDLER.setFormatter(LOG_FILE_FORMATTER)

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.WARNING)
CONSOLE_FORMATTER = logging.Formatter(fmt='{levelname}: {message}', style='{')

root_logger = logging.getLogger()
root_logger.addHandler(LOG_FILE_HANDLER)
root_logger.addHandler(CONSOLE_HANDLER)
