import logging


def get_logger(name):
    logger = logging.getLogger(name)

    if logger.handlers.__len__() != 0:
        return logger

    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s [%(filename)s:%(lineno)s %(funcName)s] - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
