from loguru import logger


def setup_logger():
    logger.add(
        'server_log.log',
        enqueue=True,
        rotation='15 MB',
        colorize=True,
        format='{time:DD-MM-YYYY HH:mm:ss.SSS} | {level} | {message}')
