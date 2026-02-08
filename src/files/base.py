from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.models.aeroplanes import Aircraft


class BaseFileHandler(ABC):
    """
    Абстрактный класс для работы с файловыми хранилищами.

    Определяет интерфейс для добавления, получения и удаления данных
    о самолетах. Может быть использован как основа для коннекторов
    к различным хранилищам (файлы, БД, удаленные хранилища).
    """

    def __init__(self, filename: str = "aircraft_data") -> None:
        """
        Инициализация файлового обработчика.

        Args:
            filename (str): Имя файла (без расширения)
        """
        self._filename = filename

    @property
    def filename(self) -> str:
        """Получить имя файла."""
        return self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        """Установить новое имя файла."""
        self._filename = value

    @abstractmethod
    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """
        Добавить информацию о самолете в файл.

        Args:
            aircraft (Aircraft): Объект самолета

        Returns:
            bool: True если успешно, False если ошибка
        """
        pass

    @abstractmethod
    def add_aircrafts(self, aircrafts: List[Aircraft]) -> bool:
        """
        Добавить список самолетов в файл.

        Args:
            aircrafts (List[Aircraft]): Список объектов самолетов

        Returns:
            bool: True если успешно, False если ошибка
        """
        pass

    @abstractmethod
    def get_all_aircrafts(self) -> List[Dict[str, Any]]:
        """
        Получить все самолеты из файла.

        Returns:
            List[Dict[str, Any]]: Список словарей с данными самолетов
        """
        pass

    @abstractmethod
    def get_aircrafts_by_country(self, country: str) -> List[Dict[str, Any]]:
        """
        Получить самолеты по стране регистрации.

        Args:
            country (str): Страна регистрации

        Returns:
            List[Dict[str, Any]]: Список самолетов указанной страны
        """
        pass

    @abstractmethod
    def get_top_aircrafts_by_altitude(self, n: int) -> List[Dict[str, Any]]:
        """
        Получить топ N самолетов по высоте полета.

        Args:
            n (int): Количество самолетов в топе

        Returns:
            List[Dict[str, Any]]: Топ N самолетов по высоте
        """
        pass

    @abstractmethod
    def delete_aircraft(self, icao24: str) -> bool:
        """
        Удалить информацию о самолете по ICAO24.

        Args:
            icao24 (str): Уникальный идентификатор самолета

        Returns:
            bool: True если успешно удалено, False если не найдено
        """
        pass

    @abstractmethod
    def clear_all_data(self) -> bool:
        """
        Удалить все данные из файла.

        Returns:
            bool: True если успешно
        """
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по данным в файле.

        Returns:
            Dict[str, Any]: Статистика
        """
        pass

    # Методы для интеграции с БД (заглушки)

    def connect(self) -> bool:
        """
        Подключиться к хранилищу.

        Returns:
            bool: True если успешно
        """
        # Заглушка для будущей интеграции с БД
        return True

    def disconnect(self) -> bool:
        """
        Отключиться от хранилища.

        Returns:
            bool: True если успешно
        """
        # Заглушка для будущей интеграции с БД
        return True

    def is_connected(self) -> bool:
        """
        Проверить подключение к хранилищу.

        Returns:
            bool: True если подключено
        """
        # Заглушка для будущей интеграции с БД
        return True
