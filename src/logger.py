import logging
from logging.handlers import RotatingFileHandler

def setup_logging(is_daemon=False):
    logger = logging.getLogger('news_aggregator')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Always add a file handler, regardless of daemon mode
    file_handler = RotatingFileHandler('news_aggregator.log', maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Add console handler only if not in daemon mode
    if not is_daemon:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
