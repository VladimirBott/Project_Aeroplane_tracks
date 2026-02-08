"""
Тесты для API модулей.
"""

import unittest
from unittest.mock import Mock, patch

from src.api.aircraft_fetcher import AircraftDataFetcher
from src.api.base_api import BaseAPI
from src.api.nominatim_client import NominatimAPI
from src.api.opensky_client import OpenSkyAPI


class TestBaseAPI(unittest.TestCase):
    """Тесты абстрактного класса BaseAPI."""

    def test_base_api_is_abstract(self):
        """Проверка, что BaseAPI абстрактный."""
        with self.assertRaises(TypeError):
            BaseAPI()  # Нельзя создать экземпляр абстрактного класса

    def test_base_api_methods_exist(self):
        """Проверка наличия абстрактных методов."""
        self.assertTrue(hasattr(BaseAPI, "_connect_to_api"))
        self.assertTrue(hasattr(BaseAPI, "get_data"))

        # Проверяем, что методы абстрактные
        self.assertTrue(getattr(BaseAPI._connect_to_api, "__isabstractmethod__", False))
        self.assertTrue(getattr(BaseAPI.get_data, "__isabstractmethod__", False))


class TestNominatimAPI(unittest.TestCase):
    """Тесты для NominatimAPI."""

    def setUp(self):
        """Настройка тестового клиента."""
        self.client = NominatimAPI()

    def test_init(self):
        """Проверка инициализации."""
        self.assertEqual(
            self.client._base_url, "https://nominatim.openstreetmap.org/search"
        )

    @patch("src.api.nominatim_client.requests.get")
    def test_connect_to_api_success(self, mock_get):
        """Тест успешного подключения к API."""
        # Мокаем ответ
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response

        result = self.client._connect_to_api("http://test.com")
        self.assertEqual(result, {"test": "data"})

    @patch("src.api.nominatim_client.requests.get")
    def test_connect_to_api_failure(self, mock_get):
        """Тест ошибки подключения к API."""
        mock_get.side_effect = Exception("Connection error")

        result = self.client._connect_to_api("http://test.com")
        self.assertIsNone(result)

    @patch("src.api.nominatim_client.NominatimAPI._connect_to_api")
    def test_get_country_coordinates_success(self, mock_connect):
        """Тест получения координат страны."""
        mock_connect.return_value = [
            {"boundingbox": ["40", "50", "-10", "10"], "name": "TestCountry"}
        ]

        result = self.client.get_country_coordinates("TestCountry")
        self.assertIsNotNone(result)
        self.assertEqual(result["country"], "TestCountry")
        self.assertEqual(result["coordinates"], ["40", "50", "-10", "10"])

    @patch("src.api.nominatim_client.NominatimAPI._connect_to_api")
    def test_get_country_coordinates_failure(self, mock_connect):
        """Тест ошибки при получении координат."""
        mock_connect.return_value = None

        result = self.client.get_country_coordinates("TestCountry")
        self.assertIsNone(result)


class TestOpenSkyAPI(unittest.TestCase):
    """Тесты для OpenSkyAPI."""

    def setUp(self):
        """Настройка тестового клиента."""
        self.client = OpenSkyAPI()

    def test_init(self):
        """Проверка инициализации."""
        self.assertEqual(
            self.client._base_url, "https://opensky-network.org/api/states/all"
        )

    @patch("src.api.opensky_client.OpenSkyAPI._connect_to_api")
    def test_get_aircraft_in_area_success(self, mock_connect):
        """Тест получения самолетов в области."""
        mock_connect.return_value = {
            "states": [
                ["id1", "callsign1", "country1"],
                ["id2", "callsign2", "country2"],
            ]
        }

        coordinates = ["40", "50", "-10", "10"]
        result = self.client.get_aircraft_in_area(coordinates)

        self.assertIsNotNone(result)
        self.assertEqual(len(result["states"]), 2)

    def test_get_aircraft_in_area_invalid_coordinates(self):
        """Тест с некорректными координатами."""
        result = self.client.get_aircraft_in_area(["40", "50"])  # Не хватает координат
        self.assertIsNone(result)


class TestAircraftDataFetcher(unittest.TestCase):
    """Тесты для AircraftDataFetcher."""

    def setUp(self):
        """Настройка тестового фетчера."""
        self.fetcher = AircraftDataFetcher()

    def test_init(self):
        """Проверка инициализации фетчера."""
        self.assertIsInstance(self.fetcher._nominatim_client, NominatimAPI)
        self.assertIsInstance(self.fetcher._opensky_client, OpenSkyAPI)
        self.assertIsNone(self.fetcher._last_result)

    @patch("src.api.aircraft_fetcher.NominatimAPI")
    @patch("src.api.aircraft_fetcher.OpenSkyAPI")
    def test_get_aircraft_data_success(self, MockOpenSkyAPI, MockNominatimAPI):
        """Тест успешного получения данных."""
        # Создаем мокированные клиенты
        mock_nominatim = Mock()
        mock_opensky = Mock()

        # Настраиваем возвращаемые значения
        mock_nominatim.get_country_coordinates.return_value = {
            "country": "TestCountry",
            "coordinates": ["40", "50", "-10", "10"],
            "country_info": {"name": "TestCountry"},
        }

        mock_opensky.get_aircraft_in_area.return_value = {
            "states": [["id1", "callsign1", "TestCountry"]]
        }

        # Подменяем клиенты в фетчере
        self.fetcher._nominatim_client = mock_nominatim
        self.fetcher._opensky_client = mock_opensky

        result = self.fetcher.get_aircraft_data("TestCountry")

        self.assertIsNotNone(result)
        self.assertEqual(result["country"], "TestCountry")
        self.assertEqual(len(result["aircraft_data"]["states"]), 1)

        # Проверяем, что методы были вызваны
        mock_nominatim.get_country_coordinates.assert_called_once_with("TestCountry")
        mock_opensky.get_aircraft_in_area.assert_called_once_with(
            ["40", "50", "-10", "10"]
        )

    @patch("src.api.aircraft_fetcher.NominatimAPI")
    @patch("src.api.aircraft_fetcher.OpenSkyAPI")
    def test_get_aircraft_data_no_coordinates(self, MockOpenSkyAPI, MockNominatimAPI):
        """Тест когда нет координат страны."""
        # Создаем мокированный клиент
        mock_nominatim = Mock()
        mock_nominatim.get_country_coordinates.return_value = None

        # Подменяем клиент в фетчере
        self.fetcher._nominatim_client = mock_nominatim

        result = self.fetcher.get_aircraft_data("UnknownCountry")
        self.assertIsNone(result)

        # Проверяем, что OpenSky не вызывался
        mock_opensky = Mock()
        self.fetcher._opensky_client = mock_opensky
        mock_opensky.get_aircraft_in_area.assert_not_called()

    @patch("src.api.aircraft_fetcher.NominatimAPI")
    @patch("src.api.aircraft_fetcher.OpenSkyAPI")
    def test_get_last_result(self, MockOpenSkyAPI, MockNominatimAPI):
        """Тест получения последнего результата."""
        # Изначально должен быть None
        self.assertIsNone(self.fetcher.get_last_result())

        # Создаем мокированные клиенты
        mock_nominatim = Mock()
        mock_opensky = Mock()

        mock_nominatim.get_country_coordinates.return_value = {
            "country": "TestCountry",
            "coordinates": ["40", "50", "-10", "10"],
            "country_info": {"name": "TestCountry"},
        }

        mock_opensky.get_aircraft_in_area.return_value = {"states": [["test_data"]]}

        self.fetcher._nominatim_client = mock_nominatim
        self.fetcher._opensky_client = mock_opensky

        # Получаем данные
        result = self.fetcher.get_aircraft_data("TestCountry")

        # Проверяем, что последний результат сохранился
        self.assertEqual(self.fetcher.get_last_result(), result)
        self.assertIsNotNone(self.fetcher._last_result)
