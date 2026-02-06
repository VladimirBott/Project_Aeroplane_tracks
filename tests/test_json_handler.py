"""
Тесты для JSONFileHandler.
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path

from src.files.json_handler import JSONFileHandler
from src.models.aeroplanes import Aircraft


class MockAircraft:
    """Мок-объект для самолета для тестов."""

    def __init__(self, **kwargs):
        self.icao24 = kwargs.get('icao24', 'default_icao')
        self.callsign = kwargs.get('callsign', 'default_callsign')
        self.origin_country = kwargs.get('origin_country', 'default_country')
        self.latitude = kwargs.get('latitude', 0.0)
        self.longitude = kwargs.get('longitude', 0.0)
        self.baro_altitude = kwargs.get('baro_altitude', 0.0)
        self.velocity = kwargs.get('velocity', 0.0)
        self.true_track = kwargs.get('true_track', 0.0)
        self.vertical_rate = kwargs.get('vertical_rate', 0.0)
        self.geo_altitude = kwargs.get('geo_altitude', 0.0)
        self.on_ground = kwargs.get('on_ground', False)
        self.squawk = kwargs.get('squawk', None)

    def to_dict(self):
        """Преобразование в словарь для тестов."""
        return {
            'icao24': self.icao24,
            'callsign': self.callsign,
            'origin_country': self.origin_country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'baro_altitude': self.baro_altitude,
            'velocity': self.velocity,
            'true_track': self.true_track,
            'vertical_rate': self.vertical_rate,
            'geo_altitude': self.geo_altitude,
            'on_ground': self.on_ground,
            'squawk': self.squawk,
        }


class TestJSONFileHandler(unittest.TestCase):
    """Тесты для JSONFileHandler."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Создаем папку data
        self.data_dir = Path(self.test_dir) / "data"
        self.data_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Очистка после каждого теста."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_init_with_default_filename(self):
        """Тест инициализации с именем файла по умолчанию."""
        handler = JSONFileHandler()

        self.assertEqual(handler.filename, "aircraft_data")
        self.assertTrue(handler.data_dir.exists())
        self.assertEqual(handler.data_dir.name, "data")

        # Проверяем что файл создан
        expected_file = handler.data_dir / "aircraft_data.json"
        self.assertTrue(expected_file.exists())

    def test_init_with_custom_filename(self):
        """Тест инициализации с пользовательским именем файла."""
        handler = JSONFileHandler("my_custom_data")

        self.assertEqual(handler.filename, "my_custom_data")

        # Проверяем что файл создан
        expected_file = handler.data_dir / "my_custom_data.json"
        self.assertTrue(expected_file.exists())

    def test_add_aircraft(self):
        """Тест добавления одного самолета."""
        handler = JSONFileHandler("test_data")

        # Создаем тестовый самолет
        aircraft = MockAircraft(
            icao24="abc123",
            callsign="TEST01",
            origin_country="Test Country",
            latitude=55.7558,
            longitude=37.6173,
            baro_altitude=10000,
            velocity=250,
            true_track=180,
            vertical_rate=5.0,
            geo_altitude=10000,
            on_ground=False,
            squawk="1234"
        )

        # Добавляем самолет
        result = handler.add_aircraft(aircraft)
        self.assertTrue(result)

        # Проверяем что данные записаны
        file_path = handler.data_dir / "test_data.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['icao24'], "abc123")
        self.assertEqual(data[0]['callsign'], "TEST01")
        self.assertEqual(data[0]['origin_country'], "Test Country")
        self.assertIn('_added_at', data[0])
        self.assertIn('_source', data[0])

    def test_add_aircraft_duplicate(self):
        """Тест добавления дублирующегося самолета."""
        handler = JSONFileHandler("test_data")

        # Создаем тестовый самолет
        aircraft = MockAircraft(
            icao24="abc123",
            callsign="TEST01",
            origin_country="Test Country"
        )

        # Первое добавление должно быть успешным
        result1 = handler.add_aircraft(aircraft)
        self.assertTrue(result1)

        # Второе добавление должно вернуть False (дубликат)
        result2 = handler.add_aircraft(aircraft)
        self.assertFalse(result2)

        # Проверяем что в файле только одна запись
        file_path = handler.data_dir / "test_data.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)

    def test_add_aircrafts(self):
        """Тест добавления нескольких самолетов."""
        handler = JSONFileHandler("test_data")

        # Создаем список самолетов
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001", origin_country="Country A"),
            MockAircraft(icao24="002", callsign="TST002", origin_country="Country B"),
            MockAircraft(icao24="003", callsign="TST003", origin_country="Country C"),
        ]

        # Добавляем самолеты
        result = handler.add_aircrafts(aircrafts)
        self.assertTrue(result)

        # Проверяем что все самолеты записаны
        file_path = handler.data_dir / "test_data.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data), 3)
        icaos = {item['icao24'] for item in data}
        self.assertEqual(icaos, {"001", "002", "003"})

    def test_add_aircrafts_with_duplicates(self):
        """Тест добавления списка с дубликатами."""
        handler = JSONFileHandler("test_data")

        # Сначала добавляем один самолет
        existing_aircraft = MockAircraft(icao24="001", callsign="EXIST", origin_country="Country A")
        handler.add_aircraft(existing_aircraft)

        # Теперь добавляем список с дубликатом
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001", origin_country="Country A"),  # Дубликат
            MockAircraft(icao24="002", callsign="TST002", origin_country="Country B"),  # Новый
        ]

        result = handler.add_aircrafts(aircrafts)
        self.assertTrue(result)

        # Проверяем что только новый самолет добавлен
        file_path = handler.data_dir / "test_data.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data), 2)  # 1 старый + 1 новый

    def test_get_all_aircrafts(self):
        """Тест получения всех самолетов."""
        handler = JSONFileHandler("test_data")

        # Добавляем несколько самолетов
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001", origin_country="Country A"),
            MockAircraft(icao24="002", callsign="TST002", origin_country="Country B"),
        ]

        handler.add_aircrafts(aircrafts)

        # Получаем все самолеты
        all_aircrafts = handler.get_all_aircrafts()

        self.assertEqual(len(all_aircrafts), 2)

        # Проверяем что служебные поля удалены
        for aircraft in all_aircrafts:
            self.assertNotIn('_added_at', aircraft)
            self.assertNotIn('_source', aircraft)

    def test_get_aircrafts_by_country(self):
        """Тест фильтрации самолетов по стране."""
        handler = JSONFileHandler("test_data")

        # Добавляем самолеты из разных стран
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001", origin_country="USA"),
            MockAircraft(icao24="002", callsign="TST002", origin_country="Russia"),
            MockAircraft(icao24="003", callsign="TST003", origin_country="USA"),
            MockAircraft(icao24="004", callsign="TST004", origin_country="Germany"),
        ]

        handler.add_aircrafts(aircrafts)

        # Получаем самолеты из USA
        usa_aircrafts = handler.get_aircrafts_by_country("USA")

        self.assertEqual(len(usa_aircrafts), 2)
        for aircraft in usa_aircrafts:
            self.assertEqual(aircraft['origin_country'], "USA")

        # Проверяем регистронезависимость
        usa_aircrafts_lower = handler.get_aircrafts_by_country("usa")
        self.assertEqual(len(usa_aircrafts_lower), 2)

    def test_get_top_aircrafts_by_altitude(self):
        """Тест получения топ N самолетов по высоте."""
        handler = JSONFileHandler("test_data")

        # Добавляем самолеты с разной высотой
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001", baro_altitude=5000),
            MockAircraft(icao24="002", callsign="TST002", baro_altitude=10000),
            MockAircraft(icao24="003", callsign="TST003", baro_altitude=3000),
            MockAircraft(icao24="004", callsign="TST004", baro_altitude=8000),
            MockAircraft(icao24="005", callsign="TST005", baro_altitude=12000),
        ]

        handler.add_aircrafts(aircrafts)

        # Получаем топ 3 по высоте
        top_3 = handler.get_top_aircrafts_by_altitude(3)

        self.assertEqual(len(top_3), 3)

        # Проверяем сортировку по убыванию высоты
        altitudes = [a['baro_altitude'] for a in top_3]
        self.assertEqual(altitudes, [12000, 10000, 8000])

        # Проверяем что возвращаются правильные самолеты
        icaos = {a['icao24'] for a in top_3}
        self.assertEqual(icaos, {"005", "002", "004"})

    def test_delete_aircraft(self):
        """Тест удаления самолета."""
        handler = JSONFileHandler("test_data")

        # Добавляем несколько самолетов
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001"),
            MockAircraft(icao24="002", callsign="TST002"),
            MockAircraft(icao24="003", callsign="TST003"),
        ]

        handler.add_aircrafts(aircrafts)

        # Удаляем один самолет
        result = handler.delete_aircraft("002")
        self.assertTrue(result)

        # Проверяем что самолет удален
        all_aircrafts = handler.get_all_aircrafts()
        self.assertEqual(len(all_aircrafts), 2)

        icaos = {a['icao24'] for a in all_aircrafts}
        self.assertEqual(icaos, {"001", "003"})

    def test_delete_nonexistent_aircraft(self):
        """Тест удаления несуществующего самолета."""
        handler = JSONFileHandler("test_data")

        # Добавляем самолет
        aircraft = MockAircraft(icao24="001", callsign="TST001")
        handler.add_aircraft(aircraft)

        # Пытаемся удалить несуществующий
        result = handler.delete_aircraft("999")
        self.assertFalse(result)  # Должно вернуть False

        # Проверяем что оригинальный самолет остался
        all_aircrafts = handler.get_all_aircrafts()
        self.assertEqual(len(all_aircrafts), 1)

    def test_clear_all_data(self):
        """Тест очистки всех данных."""
        handler = JSONFileHandler("test_data")

        # Добавляем данные
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001"),
            MockAircraft(icao24="002", callsign="TST002"),
        ]

        handler.add_aircrafts(aircrafts)

        # Проверяем что данные есть
        initial_count = handler.get_aircraft_count()
        self.assertEqual(initial_count, 2)

        # Очищаем
        result = handler.clear_all_data()
        self.assertTrue(result)

        # Проверяем что данные удалены
        final_count = handler.get_aircraft_count()
        self.assertEqual(final_count, 0)

    def test_get_statistics(self):
        """Тест получения статистики."""
        handler = JSONFileHandler("test_data")

        # Добавляем разнообразные данные для статистики
        aircrafts = [
            MockAircraft(
                icao24="001",
                origin_country="USA",
                baro_altitude=10000,
                velocity=250
            ),
            MockAircraft(
                icao24="002",
                origin_country="Russia",
                baro_altitude=8000,
                velocity=200
            ),
            MockAircraft(
                icao24="003",
                origin_country="USA",
                baro_altitude=12000,
                velocity=300
            ),
        ]

        handler.add_aircrafts(aircrafts)

        # Получаем статистику
        stats = handler.get_statistics()

        # Проверяем базовую статистику
        self.assertEqual(stats['total_aircrafts'], 3)

        # Проверяем статистику по странам
        self.assertEqual(stats['countries']['USA'], 2)
        self.assertEqual(stats['countries']['Russia'], 1)

        # Проверяем статистику высот
        self.assertEqual(stats['altitude_stats']['min'], 8000)
        self.assertEqual(stats['altitude_stats']['max'], 12000)
        self.assertAlmostEqual(stats['altitude_stats']['average'], 10000, delta=0.1)

        # Проверяем статистику скоростей
        self.assertEqual(stats['speed_stats']['min'], 200)
        self.assertEqual(stats['speed_stats']['max'], 300)
        self.assertAlmostEqual(stats['speed_stats']['average'], 250, delta=0.1)

        # Проверяем самую распространенную страну
        self.assertEqual(stats['most_common_country']['country'], "USA")
        self.assertEqual(stats['most_common_country']['count'], 2)

    def test_get_statistics_empty(self):
        """Тест статистики для пустого файла."""
        handler = JSONFileHandler("test_data")

        stats = handler.get_statistics()

        self.assertEqual(stats['total_aircrafts'], 0)
        self.assertEqual(stats['countries'], {})
        self.assertEqual(stats['file_location'], str(handler.data_dir / "test_data.json"))

    def test_get_aircraft_count(self):
        """Тест подсчета количества самолетов."""
        handler = JSONFileHandler("test_data")

        # Проверяем пустой файл
        initial_count = handler.get_aircraft_count()
        self.assertEqual(initial_count, 0)

        # Добавляем самолеты
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001"),
            MockAircraft(icao24="002", callsign="TST002"),
        ]

        handler.add_aircrafts(aircrafts)

        # Проверяем после добавления
        final_count = handler.get_aircraft_count()
        self.assertEqual(final_count, 2)

    def test_get_countries(self):
        """Тест получения списка стран."""
        handler = JSONFileHandler("test_data")

        # Добавляем самолеты из разных стран
        aircrafts = [
            MockAircraft(icao24="001", origin_country="USA"),
            MockAircraft(icao24="002", origin_country="Russia"),
            MockAircraft(icao24="003", origin_country="USA"),
            MockAircraft(icao24="004", origin_country="Germany"),
            MockAircraft(icao24="005", origin_country="France"),
        ]

        handler.add_aircrafts(aircrafts)

        # Получаем список стран
        countries = handler.get_countries()

        self.assertEqual(len(countries), 4)  # USA, Russia, Germany, France
        self.assertIn("USA", countries)
        self.assertIn("Russia", countries)
        self.assertIn("Germany", countries)
        self.assertIn("France", countries)

        # Проверяем что список отсортирован
        self.assertEqual(countries, sorted(countries))

    def test_get_file_path(self):
        """Тест получения пути к файлу."""
        handler = JSONFileHandler("test_data")

        file_path = handler.get_file_path()

        # Проверяем что путь содержит папку data и имя файла
        self.assertIn("data", file_path)
        self.assertIn("test_data.json", file_path)
        self.assertTrue(file_path.endswith(".json"))

    def test_read_corrupted_json(self):
        """Тест чтения поврежденного JSON файла."""
        handler = JSONFileHandler("test_data")

        # Намеренно портим файл
        file_path = handler.data_dir / "test_data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("{ это не валидный JSON }")

        # Попытка чтения должна создать новый файл
        data = handler._read_data()
        self.assertEqual(data, [])  # Должен вернуться пустой список

        # Проверяем что файл перезаписан
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, "[]")  # Пустой JSON массив


if __name__ == "__main__":
    unittest.main()