import logging
import sys


def setup_logger(name: str, level: str, log_file: str) -> logging.Logger:
    """
    Configures and returns a logger that prefixes messages with DEBUG:
    and includes timestamps.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter("DEBUG: %(asctime)s %(levelname)s: %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger

# # get logger
# logger = logging.getLogger()
#
# # create formatter
# formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")
#
# # create handlers
# stream_handler = logging.StreamHandler(sys.stdout)
#
# """
# remove filehandler for serverless hosting to prevent issues This error occurs because Vercel's serverless environment has a read-only filesystem,
# and your code is trying to write to a file (app.log) using logging.FileHandler
# file_handler = logging.FileHandler('app.log')
# file_handler.setFormatter(formatter)
# logger.handlers = [stream_handler, file_handler]
# """
# file_handler = logging.FileHandler('app.log')
# file_handler.setFormatter(formatter)
# logger.handlers = [stream_handler, file_handler]
# stream_handler.setFormatter(formatter)
#
# # set log level
# logger.setLevel(logging.INFO)
