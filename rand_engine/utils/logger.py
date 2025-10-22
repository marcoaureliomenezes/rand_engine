import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers and not logging.getLogger().handlers:
        logger.addHandler(logging.NullHandler())
    
    return logger
