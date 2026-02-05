"""
Главный модуль для получения данных о самолетах.
Объединяет работу с Nominatim и OpenSky API.
"""

from typing import Optional, Dict, Any
from .nominatim_client import NominatimAPI
from .opensky_client import OpenSkyAPI


class AircraftDataFetcher:
    """
    Основной класс для получения полных данных о самолетах в стране.

    Использует:
    1. NominatimAPI - для получения координат страны
    2. OpenSkyAPI - для получения данных о самолетах
    """

    def __init__(self) -> None:
        """
        Инициализация фетчера данных.

        Создает экземпляры клиентов для двух API сервисов.
        """
        self._nominatim_client: NominatimAPI = NominatimAPI()
        self._opensky_client: OpenSkyAPI = OpenSkyAPI()
        self._last_result: Optional[Dict[str, Any]] = None

    def get_aircraft_data(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Получение полных данных о самолетах в воздушном пространстве страны.

        Args:
            country (str): Название страны

        Returns:
            Optional[Dict[str, Any]]: Полные данные о стране и самолетах

        Структура возвращаемых данных:
            {
                'country': 'Canada',
                'coordinates': [...],
                'country_info': {...},
                'aircraft_data': {...}
            }
        """
        # 1. Получаем координаты страны через Nominatim
        country_info = self._nominatim_client.get_country_coordinates(country)
        if not country_info:
            print(f"Не удалось получить координаты для страны: {country}")
            return None

        coordinates = country_info['coordinates']

        # 2. Получаем данные о самолетах через OpenSky
        aircraft_data = self._opensky_client.get_aircraft_in_area(coordinates)
        if not aircraft_data:
            print(f"Не удалось получить данные о самолетах для страны: {country}")
            # Возвращаем хотя бы информацию о стране
            aircraft_data = {'states': None}

        # 3. Формируем итоговый результат
        self._last_result = {
            'country': country,
            'coordinates': coordinates,
            'country_info': country_info['country_info'],
            'aircraft_data': aircraft_data
        }

        return self._last_result

    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """
        Получение последних загруженных данных.

        Returns:
            Optional[Dict[str, Any]]: Последний результат или None
        """
        return self._last_result