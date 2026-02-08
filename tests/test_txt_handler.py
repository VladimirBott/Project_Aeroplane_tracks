"""
Тесты для TXTFileHandler.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from src.files.txt_handler import TXTFileHandler


class MockAircraft:
    """Мок-объект для самолета для тестов."""

    def __init__(self, **kwargs):
        self.icao24 = kwargs.get("icao24", "default_icao")
        self.callsign = kwargs.get("callsign", "default_callsign")
        self.origin_country = kwargs.get("origin_country", "default_country")
        self.latitude = kwargs.get("latitude", 0.0)
        self.longitude = kwargs.get("longitude", 0.0)
        self.baro_altitude = kwargs.get("baro_altitude", 0.0)
        self.velocity = kwargs.get("velocity", 0.0)
        self.true_track = kwargs.get("true_track", 0.0)
        self.vertical_rate = kwargs.get("vertical_rate", 0.0)
        self.geo_altitude = kwargs.get("geo_altitude", 0.0)
        self.on_ground = kwargs.get("on_ground", False)
        self.squawk = kwargs.get("squawk", None)

        # Свойства для форматирования
        self.altitude_feet = self.baro_altitude * 3.28084  # метры в футы
        self.velocity_kmh = self.velocity * 3.6  # м/с в км/ч


class TestTXTFileHandler(unittest.TestCase):
    """Тесты для TXTFileHandler."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Очистка после каждого теста."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_init_with_default_filename(self):
        """Тест инициализации с именем файла по умолчанию."""
        handler = TXTFileHandler()

        self.assertEqual(handler.filename, "aircraft_data")

        # Проверяем что файл создан
        expected_file = "aircraft_data.txt"
        self.assertTrue(os.path.exists(expected_file))

        # Проверяем содержимое файла
        with open(expected_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("=== Aviation Tracker Data ===", content)

    def test_init_with_custom_filename(self):
        """Тест инициализации с пользовательским именем файла."""
        handler = TXTFileHandler("my_custom_data")

        self.assertEqual(handler.filename, "my_custom_data")

        # Проверяем что файл создан
        expected_file = "my_custom_data.txt"
        self.assertTrue(os.path.exists(expected_file))

    def test_add_aircraft(self):
        """Тест добавления одного самолета в TXT."""
        handler = TXTFileHandler("test_data")

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
            squawk="1234",
        )

        # Добавляем самолет
        result = handler.add_aircraft(aircraft)
        self.assertTrue(result)

        # Проверяем содержимое файла
        file_path = "test_data.txt"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Проверяем что основные данные записаны
        self.assertIn("Самолет: TEST01 (abc123)", content)
        self.assertIn("Страна: Test Country", content)
        self.assertIn("Координаты: 55.7558°N, 37.6173°E", content)
        self.assertIn("Высота: 10000 м", content)
        self.assertIn("Скорость: 250 м/с", content)
        self.assertIn("Курс: 180°", content)
        self.assertIn("Вертикальная скорость: 5.0 м/с", content)
        self.assertIn("На земле: Нет", content)
        self.assertIn("Squawk: 1234", content)
        self.assertIn("Добавлено:", content)

    def test_add_aircraft_without_squawk(self):
        """Тест добавления самолета без squawk."""
        handler = TXTFileHandler("test_data")

        # Создаем самолет без squawk
        aircraft = MockAircraft(
            icao24="abc123",
            callsign="TEST01",
            origin_country="Test Country",
            squawk=None,  # Без squawk
        )

        # Добавляем самолет
        result = handler.add_aircraft(aircraft)
        self.assertTrue(result)

        # Проверяем что строка с squawk не добавлена
        file_path = "test_data.txt"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertNotIn("Squawk:", content)

    def test_add_aircraft_on_ground(self):
        """Тест добавления самолета на земле."""
        handler = TXTFileHandler("test_data")

        # Создаем самолет на земле
        aircraft = MockAircraft(
            icao24="abc123",
            callsign="TEST01",
            origin_country="Test Country",
            on_ground=True,
        )

        # Добавляем самолет
        result = handler.add_aircraft(aircraft)
        self.assertTrue(result)

        # Проверяем что статус правильный
        file_path = "test_data.txt"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("На земле: Да", content)

    def test_add_aircrafts(self):
        """Тест добавления нескольких самолетов в TXT."""
        handler = TXTFileHandler("test_data")

        # Сначала очистим файл чтобы начать с чистого состояния
        handler.clear_all_data()

        # Создаем список самолетов
        aircrafts = [
            MockAircraft(icao24="001", callsign="TST001", origin_country="Country A"),
            MockAircraft(icao24="002", callsign="TST002", origin_country="Country B"),
            MockAircraft(icao24="003", callsign="TST003", origin_country="Country C"),
        ]

        # Добавляем самолеты
        result = handler.add_aircrafts(aircrafts)
        self.assertTrue(result)

        # Проверяем содержимое файла
        file_path = "test_data.txt"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Проверяем что все самолеты записаны
        self.assertIn("TST001 (001)", content)
        self.assertIn("TST002 (002)", content)
        self.assertIn("TST003 (003)", content)

        # Считаем сколько раз встречается каждая строка с вызовом
        # Вместо подсчета разделителей, просто проверяем наличие каждого самолета
        for aircraft in aircrafts:
            self.assertIn(aircraft.callsign, content)
            self.assertIn(aircraft.icao24, content)

        # Проверяем что количество записей правильное
        # Поскольку каждый самолет записывается с вызовом add_aircraft,
        # а он добавляет разделитель и данные, просто убедимся что есть все 3 записи
        # Подсчитаем сколько раз встречается фраза "Самолет:" (должно быть 3 раза)
        aircraft_count = content.count("Самолет:")
        self.assertEqual(aircraft_count, 3)

    def test_add_aircraft_partial_failure(self):
        """Тест добавления списка с частичным сбоем."""
        handler = TXTFileHandler("test_data")

        # Мокаем метод add_aircraft чтобы имитировать частичный сбой
        with patch.object(handler, "add_aircraft") as mock_add:
            mock_add.side_effect = [
                True,
                False,
                True,
            ]  # Первый и третий успешны, второй нет

            # Создаем список самолетов
            aircrafts = [
                MockAircraft(icao24="001", callsign="TST001"),
                MockAircraft(icao24="002", callsign="TST002"),
                MockAircraft(icao24="003", callsign="TST003"),
            ]

            result = handler.add_aircrafts(aircrafts)

            # Проверяем что метод вызывался 3 раза
            self.assertEqual(mock_add.call_count, 3)
            # Результат должен быть False так как один вызов неудачный
            self.assertFalse(result)

    def test_clear_all_data(self):
        """Тест очистки TXT файла."""
        handler = TXTFileHandler("test_data")

        # Добавляем данные
        aircraft = MockAircraft(icao24="001", callsign="TST001")
        handler.add_aircraft(aircraft)

        # Проверяем что данные есть
        file_path = "test_data.txt"
        with open(file_path, "r", encoding="utf-8") as f:
            content_before = f.read()

        self.assertIn("TST001 (001)", content_before)

        # Очищаем
        result = handler.clear_all_data()
        self.assertTrue(result)

        # Проверяем что файл очищен
        with open(file_path, "r", encoding="utf-8") as f:
            content_after = f.read()

        self.assertNotIn("TST001 (001)", content_after)
        self.assertIn("=== Aviation Tracker Data ===", content_after)

    def test_get_all_aircrafts_txt_not_supported(self):
        """Тест что get_all_aircrafts не поддерживается для TXT."""
        handler = TXTFileHandler("test_data")

        # Метод должен вернуть пустой список и напечатать предупреждение
        with patch("builtins.print") as mock_print:
            result = handler.get_all_aircrafts()

            self.assertEqual(result, [])
            mock_print.assert_called_with(
                "Внимание: TXT формат не поддерживает полноценное чтение структурированных данных"
            )

    def test_file_creation_on_init(self):
        """Тест создания файла при инициализации."""
        # Удаляем файл если существует
        test_file = "test_creation.txt"
        if os.path.exists(test_file):
            os.remove(test_file)

        # Инициализируем обработчик
        TXTFileHandler("test_creation")

        # Проверяем что файл создан
        self.assertTrue(os.path.exists("test_creation.txt"))

        # Проверяем начальное содержимое
        with open("test_creation.txt", "r", encoding="utf-8") as f:
            content = f.read()

        expected_start = "=== Aviation Tracker Data ===\n\n"
        self.assertTrue(content.startswith(expected_start))


if __name__ == "__main__":
    unittest.main()
