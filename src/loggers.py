import logging
import os

FORMAT_LOG = "%(asctime)s  %(module)s.%(funcName)s - %(levelname)s: %(message)s"
FORMAT_DATE_LOG = "%Y-%m-%d %H:%M:%S"


def create_logger(name_logger: str, name_log_file: str, logging_level: int) -> logging.Logger:
    """Функция создания логера для модулей"""
    logger = logging.getLogger(name_logger)
    logger.setLevel(logging_level)

    logs_path = os.path.join(os.path.dirname(__file__), "..\\logs\\")

    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    file_handler = logging.FileHandler(os.path.join(logs_path, name_log_file), mode="w", encoding="utf-8")
    file_handler.setLevel(logging_level)

    file_formatter = logging.Formatter(FORMAT_LOG, FORMAT_DATE_LOG)

    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    return logger
