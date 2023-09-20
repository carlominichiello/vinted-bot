import logging
import os

from termcolor import colored

import src.defaults as defaults
from src.logger.formatters import ColoredFormatter


def setup(logger_name, config):
    logger = logging.getLogger(logger_name)

    logger.setLevel(
        config["log_level"]
    ) if "log_level" in config else defaults.default_log_level

    time_color = "cyan"
    formatter = ColoredFormatter(
        fmt=colored("%(asctime)s", time_color) + " - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logs_dir = (
        config["logs_directory"]
        if "logs_directory" in config
        else defaults.default_logs_directory
    )
    if not os.path.isdir(logs_dir):
        os.makedirs(logs_dir)
    file_handler = logging.FileHandler(f"{os.path.join(logs_dir, logger_name)}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
