from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from src.models.aeroplanes import Aircraft


class BaseFileHandler(ABC):
    """
    Простой абстрактный класс для работы с файлами.
    """

    def __init__(self, filename: str = "aircraft_data") -> None:
        """
        Инициализация файлового обработчика.

        Args:
            filename (str): Имя файла (без расширения)
        """
        self._filename = filename
        # Просто создаем папку data в текущей директории
        self.data_dir = Path.cwd() / "data"
        self.data_dir.mkdir(exist_ok=True)

    @property
    def full_path(self) -> Path:
        """Полный путь к файлу."""
        return self.data_dir / f"{self._filename}{self.file_extension}"

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Расширение файла."""
        pass

    @abstractmethod
    def add_aircraft(self, aircraft: Aircraft) -> bool:
        pass

    @abstractmethod
    def add_aircrafts(self, aircrafts: List[Aircraft]) -> bool:
        pass

    @abstractmethod
    def get_all_aircrafts(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_aircrafts_by_country(self, country: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_top_aircrafts_by_altitude(self, n: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_aircraft(self, icao24: str) -> bool:
        pass

    @abstractmethod
    def clear_all_data(self) -> bool:
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        pass
