"""
Модуль для работы с файлами различных форматов.
"""

from .base import BaseFileHandler
from .json_handler import JSONFileHandler
from .txt_handler import TXTFileHandler

__all__ = ["BaseFileHandler", "JSONFileHandler", "TXTFileHandler"]
