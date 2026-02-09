"""
API модуль для взаимодействия с внешними сервисами.

Экспортирует:
- BaseAPI: Абстрактный базовый класс
- NominatimAPI: Клиент для OpenStreetMap
- OpenSkyAPI: Клиент для OpenSky Network
- AircraftDataFetcher: Главный класс для получения данных о самолетах
"""

from src.api.aircraft_fetcher import AircraftDataFetcher
from src.api.base_api import BaseAPI

from .nominatim_client import NominatimAPI
from .opensky_client import OpenSkyAPI

__all__ = ["BaseAPI", "NominatimAPI", "OpenSkyAPI", "AircraftDataFetcher"]
"""
Основной пакет приложения Aviation Tracker.
"""

__version__ = "1.0.0"
__author__ = "Aviation Tracker Project"
