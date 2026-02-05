"""
Модуль для работы с OpenSky Network API.
"""

from typing import Optional, Dict, Any, List
from src.api.base_api import BaseAPI
import requests


class OpenSkyAPI(BaseAPI):
    """
    Класс для работы с OpenSky Network API.

    Наследуется от BaseAPI и реализует методы для получения
    данных о самолетах в реальном времени.
    """

    def __init__(self) -> None:
        """Инициализация клиента OpenSky API."""
        self._base_url: str = 'https://opensky-network.org/api/states/all'

    def _connect_to_api(self, url: str, params: Optional[Dict] = None,
                        headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Приватный метод для подключения к OpenSky API.

        Args:
            url (str): URL API endpoint
            params (Optional[Dict]): Параметры запроса
            headers (Optional[Dict]): Заголовки запроса

        Returns:
            Optional[Dict[str, Any]]: Ответ от API или None при ошибке
        """
        try:
            response = requests.get(
                url=url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к OpenSky API: {e}")
            return None

    def get_data(self, lamin: str, lamax: str, lomin: str, lomax: str) -> Optional[Dict[str, Any]]:
        """
        Получение данных о самолетах в заданной области.

        Args:
            lamin (str): Минимальная широта
            lamax (str): Максимальная широта
            lomin (str): Минимальная долгота
            lomax (str): Максимальная долгота

        Returns:
            Optional[Dict[str, Any]]: Данные о самолетах или None
        """
        params: Dict[str, str] = {
            'lamin': lamin,
            'lamax': lamax,
            'lomin': lomin,
            'lomax': lomax,
        }

        return self._connect_to_api(self._base_url, params)

    def get_aircraft_in_area(self, coordinates: List[str]) -> Optional[Dict[str, Any]]:
        """
        Специализированный метод для получения самолетов в области.

        Args:
            coordinates (List[str]): Список координат [lat_min, lat_max, lon_min, lon_max]

        Returns:
            Optional[Dict[str, Any]]: Данные о самолетах или None
        """
        if len(coordinates) != 4:
            print("Неверный формат координат")
            return None

        return self.get_data(
            lamin=coordinates[0],
            lamax=coordinates[1],
            lomin=coordinates[2],
            lomax=coordinates[3]
        )