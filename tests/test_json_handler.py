"""
Минималистичные тесты для JSONFileHandler без создания файлов.
"""
import json
from unittest.mock import MagicMock, mock_open, patch
from src.files.json_handler import JSONFileHandler
from src.models.aeroplanes import Aircraft


class TestJSONFileHandlerSimple:
    """Простые тесты для JSONFileHandler, которые не создают файлы."""

    def test_create_handler_without_files(self):
        """Просто создаем handler без файловых операций."""
        # Патчим Path в base.py, а не в json_handler
        with patch("src.files.base.Path") as MockPath:
            mock_path_instance = MockPath.return_value
            mock_path_instance.exists.return_value = True

            # Мокаем open чтобы ничего не записывать
            with patch("builtins.open", mock_open()):
                handler = JSONFileHandler("test_data")

                # Проверяем что handler создан
                assert handler is not None
                # Проверяем что это JSONFileHandler
                assert isinstance(handler, JSONFileHandler)

    def test_read_data_mocked(self):
        """Тест чтения данных с моком."""
        # Создаем mock данные
        test_data = [
            {"icao24": "A0B1C2", "callsign": "SU123"},
            {"icao24": "D3E4F5", "callsign": "BA456"},
        ]

        # Создаем handler через конструктор с моками
        with patch("src.files.base.Path") as MockPath:
            mock_path = MockPath.return_value
            mock_path.exists.return_value = True

            with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
                handler = JSONFileHandler("test")

                # Теперь можно тестировать
                with patch.object(handler, "_ensure_file_exists"):
                    result = handler._read_data()

                    assert result == test_data


class TestJSONFileHandlerMethods:
    """Тесты методов JSONFileHandler без файловых операций."""

    def setup_method(self):
        """Создаем handler без файловых операций."""
        # Создаем handler через __new__, чтобы избежать __init__
        self.handler = JSONFileHandler.__new__(JSONFileHandler)
        self.handler._filename = "test"

        # Мокаем свойства которые нужны для работы
        self.handler._read_data = MagicMock()
        self.handler._write_data = MagicMock(return_value=True)

    def test_add_aircraft(self):
        """Тест добавления самолета."""
        plane = Aircraft(icao24="A0B1C2", callsign="SU123")

        # Настраиваем мок чтения (файл пустой)
        self.handler._read_data.return_value = []

        result = self.handler.add_aircraft(plane)

        assert result is True
        self.handler._write_data.assert_called_once()

        # Проверяем что в данные добавились правильные поля
        written_data = self.handler._write_data.call_args[0][0]
        assert len(written_data) == 1
        assert written_data[0]["icao24"] == "A0B1C2"
        assert written_data[0]["callsign"] == "SU123"
        assert "_added_at" in written_data[0]

    def test_add_aircraft_already_exists(self):
        """Тест добавления уже существующего самолета."""
        plane = Aircraft(icao24="A0B1C2")

        # Настраиваем мок чтения (самолет уже есть)
        self.handler._read_data.return_value = [{"icao24": "A0B1C2"}]

        result = self.handler.add_aircraft(plane)

        assert result is False
        self.handler._write_data.assert_not_called()

    def test_get_all_aircrafts(self):
        """Тест получения всех самолетов."""
        test_data = [
            {"icao24": "A0B1C2", "callsign": "SU123", "_added_at": "2024-01-01"},
            {"icao24": "D3E4F5", "callsign": "BA456", "_added_at": "2024-01-01"},
        ]

        self.handler._read_data.return_value = test_data

        result = self.handler.get_all_aircrafts()

        assert len(result) == 2
        # Проверяем что служебные поля удалены
        for item in result:
            assert "_added_at" not in item

    def test_get_aircrafts_by_country(self):
        """Тест получения по стране."""
        test_data = [
            {"icao24": "A0B1C2", "origin_country": "Russia", "_added_at": "2024-01-01"},
            {"icao24": "D3E4F5", "origin_country": "UK", "_added_at": "2024-01-01"},
            {"icao24": "G7H8I9", "origin_country": "Russia", "_added_at": "2024-01-01"},
        ]

        self.handler._read_data.return_value = test_data

        result = self.handler.get_aircrafts_by_country("Russia")

        assert len(result) == 2
        for item in result:
            assert item["origin_country"] == "Russia"
            assert "_added_at" not in item

    def test_get_top_aircrafts_by_altitude(self):
        """Тест получения топ N по высоте."""
        test_data = [
            {"icao24": "A0B1C2", "baro_altitude": 5000, "_added_at": "2024-01-01"},
            {"icao24": "D3E4F5", "baro_altitude": 10000, "_added_at": "2024-01-01"},
            {"icao24": "G7H8I9", "baro_altitude": 7000, "_added_at": "2024-01-01"},
        ]

        self.handler._read_data.return_value = test_data

        result = self.handler.get_top_aircrafts_by_altitude(2)

        assert len(result) == 2
        # Проверяем сортировку
        assert result[0]["baro_altitude"] == 10000
        assert result[1]["baro_altitude"] == 7000

    def test_delete_aircraft(self):
        """Тест удаления самолета."""
        test_data = [
            {"icao24": "A0B1C2", "callsign": "SU123"},
            {"icao24": "D3E4F5", "callsign": "BA456"},
        ]

        self.handler._read_data.return_value = test_data

        result = self.handler.delete_aircraft("A0B1C2")

        assert result is True
        self.handler._write_data.assert_called_once()

        # Проверяем что правильный самолет удален
        written_data = self.handler._write_data.call_args[0][0]
        assert len(written_data) == 1
        assert written_data[0]["icao24"] == "D3E4F5"

    def test_clear_all_data(self):
        """Тест очистки всех данных."""
        result = self.handler.clear_all_data()

        assert result is True
        self.handler._write_data.assert_called_once_with([])

    def test_get_statistics(self):
        """Тест статистики."""
        test_data = [
            {
                "icao24": "A0B1C2",
                "origin_country": "Russia",
                "baro_altitude": 5000,
                "velocity": 200,
            },
            {
                "icao24": "D3E4F5",
                "origin_country": "UK",
                "baro_altitude": 10000,
                "velocity": 250,
            },
            {
                "icao24": "G7H8I9",
                "origin_country": "Russia",
                "baro_altitude": 7000,
                "velocity": 150,
            },
        ]

        self.handler._read_data.return_value = test_data

        stats = self.handler.get_statistics()

        assert stats["total_aircrafts"] == 3
        assert stats["most_common_country"]["country"] == "Russia"
        assert stats["most_common_country"]["count"] == 2
        assert stats["altitude_stats"]["min"] == 5000
        assert stats["altitude_stats"]["max"] == 10000
        assert stats["altitude_stats"]["average"] == (5000 + 10000 + 7000) / 3


class TestJSONFileHandlerIntegration:
    """Интеграционные тесты без реальных файлов."""

    def test_full_workflow(self):
        """Тест полного цикла работы."""
        # Создаем handler без конструктора
        handler = JSONFileHandler.__new__(JSONFileHandler)
        handler._filename = "test"

        # Создаем моки для всех методов
        read_data_mock = MagicMock()
        write_data_mock = MagicMock(return_value=True)

        handler._read_data = read_data_mock
        handler._write_data = write_data_mock

        # Самолеты для теста
        planes = [
            Aircraft(
                icao24="A0B1C2",
                callsign="SU123",
                origin_country="Russia",
                baro_altitude=10000,
            ),
            Aircraft(
                icao24="D3E4F5",
                callsign="BA456",
                origin_country="UK",
                baro_altitude=12000,
            ),
        ]

        # Настраиваем последовательные вызовы read_data
        read_data_mock.side_effect = [
            [],  # 1. Файл пустой при добавлении
            [  # 2. После добавления
                {
                    "icao24": "A0B1C2",
                    "callsign": "SU123",
                    "origin_country": "Russia",
                    "baro_altitude": 10000,
                },
                {
                    "icao24": "D3E4F5",
                    "callsign": "BA456",
                    "origin_country": "UK",
                    "baro_altitude": 12000,
                },
            ],
            [  # 3. Для get_aircrafts_by_country
                {
                    "icao24": "A0B1C2",
                    "callsign": "SU123",
                    "origin_country": "Russia",
                    "baro_altitude": 10000,
                },
                {
                    "icao24": "D3E4F5",
                    "callsign": "BA456",
                    "origin_country": "UK",
                    "baro_altitude": 12000,
                },
            ],
            [  # 4. Для get_top_aircrafts_by_altitude
                {
                    "icao24": "A0B1C2",
                    "callsign": "SU123",
                    "origin_country": "Russia",
                    "baro_altitude": 10000,
                },
                {
                    "icao24": "D3E4F5",
                    "callsign": "BA456",
                    "origin_country": "UK",
                    "baro_altitude": 12000,
                },
            ],
            [  # 5. Для get_statistics
                {
                    "icao24": "A0B1C2",
                    "callsign": "SU123",
                    "origin_country": "Russia",
                    "baro_altitude": 10000,
                },
                {
                    "icao24": "D3E4F5",
                    "callsign": "BA456",
                    "origin_country": "UK",
                    "baro_altitude": 12000,
                },
            ],
            [  # 6. Для delete_aircraft (перед удалением)
                {
                    "icao24": "A0B1C2",
                    "callsign": "SU123",
                    "origin_country": "Russia",
                    "baro_altitude": 10000,
                },
                {
                    "icao24": "D3E4F5",
                    "callsign": "BA456",
                    "origin_country": "UK",
                    "baro_altitude": 12000,
                },
            ],
            [  # 7. После удаления
                {
                    "icao24": "D3E4F5",
                    "callsign": "BA456",
                    "origin_country": "UK",
                    "baro_altitude": 12000,
                }
            ],
        ]

        # Тестируем весь цикл
        # 1. Добавляем самолеты
        assert handler.add_aircrafts(planes) is True
        assert write_data_mock.call_count == 1

        # 2. Получаем все самолеты
        all_planes = handler.get_all_aircrafts()
        assert len(all_planes) == 2

        # 3. Получаем по стране
        russian_planes = handler.get_aircrafts_by_country("Russia")
        assert len(russian_planes) == 1

        # 4. Получаем топ по высоте
        top_planes = handler.get_top_aircrafts_by_altitude(1)
        assert len(top_planes) == 1
        assert top_planes[0]["icao24"] == "D3E4F5"

        # 5. Получаем статистику
        stats = handler.get_statistics()
        assert stats["total_aircrafts"] == 2

        # 6. Удаляем самолет
        assert handler.delete_aircraft("A0B1C2") is True
        assert write_data_mock.call_count == 2

        # 7. Очищаем все
        assert handler.clear_all_data() is True
        assert write_data_mock.call_count == 3
        write_data_mock.assert_called_with([])


# Еще более простые тесты - вообще без моков
def test_json_handler_methods_exist():
    """Просто проверяем что у класса есть нужные методы."""
    assert hasattr(JSONFileHandler, "add_aircraft")
    assert hasattr(JSONFileHandler, "add_aircrafts")
    assert hasattr(JSONFileHandler, "get_all_aircrafts")
    assert hasattr(JSONFileHandler, "get_aircrafts_by_country")
    assert hasattr(JSONFileHandler, "get_top_aircrafts_by_altitude")
    assert hasattr(JSONFileHandler, "delete_aircraft")
    assert hasattr(JSONFileHandler, "clear_all_data")
    assert hasattr(JSONFileHandler, "get_statistics")


def test_json_handler_properties():
    """Проверяем свойства."""
    # Патчим чтобы избежать создания файлов
    with patch("src.files.base.Path") as MockPath:
        mock_path = MockPath.return_value
        mock_path.exists.return_value = True

        with patch("builtins.open", mock_open()):
            handler = JSONFileHandler("test")

            # Проверяем свойства
            assert hasattr(handler, "file_extension")
            assert handler.file_extension == ".json"


if __name__ == "__main__":
    # Простой запуск
    print("🧪 Запуск упрощенных тестов JSONFileHandler...")

    # Создаем экземпляры тестовых классов
    test_classes = [
        TestJSONFileHandlerSimple(),
        TestJSONFileHandlerMethods(),
        TestJSONFileHandlerIntegration(),
    ]

    passed = 0
    failed = 0

    for tester in test_classes:
        print(f"\n📋 Тестируем {tester.__class__.__name__}...")

        # Находим все методы test_
        test_methods = [
            method
            for method in dir(tester)
            if method.startswith("test_") and callable(getattr(tester, method))
        ]

        for method_name in test_methods:
            method = getattr(tester, method_name)
            try:
                # Вызываем setup_method если есть
                if hasattr(tester, "setup_method"):
                    tester.setup_method()

                method()
                print(f"  ✅ {method_name}")
                passed += 1

            except AssertionError as e:
                print(f"  ❌ {method_name}: {e}")
                failed += 1
            except Exception as e:
                print(f"  💥 {method_name}: {e}")
                failed += 1

    # Тесты-функции
    print(f"\n📋 Тестируем функции...")
    for test_func in [test_json_handler_methods_exist, test_json_handler_properties]:
        try:
            test_func()
            print(f"  ✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"  💥 {test_func.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"📊 Итог: {passed} прошло, {failed} упало")

    if failed == 0:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("❌ Есть неудачные тесты")
