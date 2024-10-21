import logging
from colorlog import ColoredFormatter
import os

def setup_logger(logger_name, log_file, level=logging.INFO):
    # Function to set up a logger with color output and file logging.
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Create color formatter
    color_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # Create console handler and set formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)

    # Create file handler and set formatter
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger("logger", "logs/run.log")

