# (c) 2023, Oliver Graebner, oliver.graebner@zohomail.eu

import logging
from logging.handlers import RotatingFileHandler

loggerName = "hg-data-pull"
loggerFormat = '%(asctime)s %(levelname)s %(threadName)-10s: %(message)s'

def getGlobalLogger() -> logging.Logger:
    return logging.getLogger(loggerName)


def setupGlobalLogger() -> logging.Logger:
    """
    Create logging facility with rotating file appender and verbose logging
    """
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    rfh = RotatingFileHandler("hg-data-pull.log", maxBytes=(1014*1240*10), backupCount=5)
    rfh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(loggerFormat)
    rfh.setFormatter(formatter)
    logger.addHandler(rfh)
    return logger

def configureStreamLogging(logLevel : int):
    """
    Configures the stream hander for the logger
    """
    logger = logging.getLogger(loggerName)
    ch = logging.StreamHandler()
    ch.setLevel(logLevel)
    formatter = logging.Formatter(loggerFormat)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug(f'Set console logging to level {logging.getLevelName(logLevel)}')

def getLoggingLevelFromConfig(config: dict()) -> int:
    """
    Get the logging level from the config or a default value if not set
    """
    ll = -1
    if "log_level" in config:
        match config['log_level']:
            case "DEBUG":
                ll = logging.DEBUG
            case "INFO":
                ll = logging.INFO
            case "WARNING":
                ll = logging.WARNING
            case "ERROR":
                ll = logging.ERROR
            case "CRITICAL":
                ll = logging.CRITICAL
            case _:
                logging.warning(f'Setting log level from config to INFO due to unknown log level {config["log_level"]}')
                ll = logging.INFO
    return ll