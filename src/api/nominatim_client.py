"""
Модуль для работы с OpenStreetMap Nominatim API.
"""

from typing import Optional, Dict, Any
from src.api.base_api import BaseAPI
import requests


class NominatimAPI(BaseAPI):
    """
    Класс для работы с OpenStreetMap Nominatim API.

    Наследуется от BaseAPI и реализует методы для получения
    географических данных о странах.
    """

    def __init__(self) -> None:
        """Инициализация клиента Nominatim API."""
        self._base_url: str = 'https://nominatim.openstreetmap.org/search'

    def _connect_to_api(self, url: str, params: Optional[Dict] = None,
                        headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Приватный метод для подключения к Nominatim API.

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
            print(f"Ошибка подключения к Nominatim API: {e}")
            return None

    def get_data(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Получение географических данных о стране.

        Args:
            country (str): Название страны

        Returns:
            Optional[Dict[str, Any]]: Данные о стране или None
        """
        headers: Dict[str, str] = {'User-Agent': 'aviation-tracker/1.0'}
        params: Dict[str, str | int] = {
            'country': country,
            'format': 'json',
            'limit': 1,
        }

        data = self._connect_to_api(self._base_url, params, headers)

        if data and isinstance(data, list) and len(data) > 0:
            return data[0]

        return None

    def get_country_coordinates(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Специализированный метод для получения координат страны.

        Args:
            country (str): Название страны

        Returns:
            Optional[Dict[str, Any]]: Словарь с координатами и информацией о стране
        """
        country_data = self.get_data(country)

        if not country_data:
            return None

        coordinates = country_data.get('boundingbox')
        if coordinates and len(coordinates) == 4:
            return {
                'country': country,
                'coordinates': coordinates,
                'country_info': country_data
            }

        return None