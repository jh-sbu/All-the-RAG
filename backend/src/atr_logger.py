import logging


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
fmt = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(filename)-16s: %(lineno)-5d | %(message)s"
)
handler.setFormatter(fmt)
logger.addHandler(handler)


def get_logger():
    return logger


def set_log_level(log_level: int):
    logger.setLevel(log_level)
    for handler in logger.handlers:
        handler.setLevel(log_level)
