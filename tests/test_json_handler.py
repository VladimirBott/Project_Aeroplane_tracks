"""
Тесты для модуля JSONFileHandler.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.files.json_handler import JSONFileHandler
from src.models.aeroplanes import Aircraft


def create_test_aircraft(
    icao24="test123",
    callsign="TEST",
    origin_country="Test Country",
    latitude=55.7558,
    longitude=37.6173,
    baro_altitude=10000.0,
    velocity=250.0,
    on_ground=False,
    squawk="1234",
    true_track=45.0,
    vertical_rate=10.0,
    geo_altitude=9500.0,
):
    """Создать тестовый самолет с заданными параметрами."""
    return Aircraft(
        icao24=icao24,
        callsign=callsign,
        origin_country=origin_country,
        latitude=latitude,
        longitude=longitude,
        baro_altitude=baro_altitude,
        velocity=velocity,
        on_ground=on_ground,
        squawk=squawk,
        true_track=true_track,
        vertical_rate=vertical_rate,
        geo_altitude=geo_altitude,
    )


@pytest.fixture
def temp_dir():
    """Создать временную директорию для тестов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_aircraft():
    """Создать тестовый объект самолета."""
    return create_test_aircraft(
        icao24="abc123", callsign="TEST01", origin_country="Test Country"
    )


@pytest.fixture
def sample_aircraft_dict():
    """Создать тестовый словарь самолета."""
    return {
        "icao24": "def456",
        "callsign": "TEST02",
        "origin_country": "Another Country",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "baro_altitude": 8000.0,
        "velocity": 220.0,
        "on_ground": True,
        "squawk": "5678",
        "true_track": 90.0,
        "vertical_rate": 0.0,
        "geo_altitude": 7800.0,
    }


class TestJSONFileHandler:
    """Тесты для класса JSONFileHandler."""

    def test_init_creates_data_dir(self, temp_dir):
        """Тест инициализации создает папку data."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")

            # Проверяем что папка создана
            data_dir = temp_dir / "data"
            assert data_dir.exists()

            # Проверяем путь к файлу
            expected_file = data_dir / "test_data.json"
            assert handler._full_filename == expected_file

    def test_init_creates_file_if_not_exists(self, temp_dir):
        """Тест создания файла если он не существует."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")

            # Проверяем что файл создан
            assert handler._full_filename.exists()

            # Проверяем содержимое файла
            with open(handler._full_filename, "r", encoding="utf-8") as f:
                content = json.load(f)
                assert content == []

    def test_init_uses_existing_file(self, temp_dir):
        """Тест использования существующего файла."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            # Создаем файл с данными заранее
            data_dir = temp_dir / "data"
            data_dir.mkdir(exist_ok=True)

            test_data = [{"test": "data"}]
            file_path = data_dir / "test_data.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(test_data, f)

            # Создаем handler
            handler = JSONFileHandler("test_data")

            # Проверяем что файл существует и не перезаписан
            assert handler._full_filename.exists()
            assert handler._full_filename == file_path

    def test_read_data_empty_file(self, temp_dir):
        """Тест чтения пустого файла."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")

            # Мокаем logger чтобы не засорять вывод
            handler.logger = Mock()

            data = handler._read_data()
            assert data == []

    def test_read_data_with_content(self, temp_dir):
        """Тест чтения файла с содержимым."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            # Создаем файл с данными
            data_dir = temp_dir / "data"
            data_dir.mkdir(exist_ok=True)

            test_data = [
                {"icao24": "test1", "name": "Test 1"},
                {"icao24": "test2", "name": "Test 2"},
            ]

            file_path = data_dir / "test_data.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(test_data, f)

            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            data = handler._read_data()
            assert data == test_data

    def test_read_data_invalid_json(self, temp_dir):
        """Тест чтения невалидного JSON файла."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            # Записываем невалидный JSON в файл
            with open(handler._full_filename, "w", encoding="utf-8") as f:
                f.write("not a valid json")

            data = handler._read_data()
            assert data == []

            # Проверяем что файл был исправлен
            with open(handler._full_filename, "r", encoding="utf-8") as f:
                content = f.read().strip()
                assert content == "[]"

    def test_write_data_success(self, temp_dir):
        """Тест успешной записи данных."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [{"test": "data"}]
            result = handler._write_data(test_data)

            assert result is True
            assert handler._full_filename.exists()

            # Проверяем записанные данные
            with open(handler._full_filename, "r", encoding="utf-8") as f:
                content = json.load(f)
                assert content == test_data

    def test_write_data_permission_error(self, temp_dir):
        """Тест записи при ошибке прав доступа."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            # Мокаем os.access чтобы симулировать ошибку прав
            with patch("os.access", return_value=False):
                test_data = [{"test": "data"}]
                result = handler._write_data(test_data)

                assert result is False

    def test_aircraft_exists(self):
        """Тест проверки существования самолета."""
        handler = JSONFileHandler()
        handler.logger = Mock()

        test_data = [
            {"icao24": "abc123", "name": "Test 1"},
            {"icao24": "def456", "name": "Test 2"},
        ]

        # Самолет существует
        assert handler._aircraft_exists("abc123", test_data) is True
        assert handler._aircraft_exists("def456", test_data) is True

        # Самолет не существует
        assert handler._aircraft_exists("xyz789", test_data) is False

    def test_add_aircraft_duplicate(self, temp_dir, sample_aircraft):
        """Тест добавления дубликата самолета."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            existing_data = [{"icao24": "abc123", "name": "Existing"}]

            with patch.object(handler, "_read_data", return_value=existing_data):
                result = handler.add_aircraft(sample_aircraft)
                assert result is False

    def test_add_aircrafts_empty_list(self, temp_dir):
        """Тест добавления пустого списка самолетов."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            result = handler.add_aircrafts([])
            assert result is True

    def test_get_all_aircrafts(self, temp_dir):
        """Тест получения всех самолетов."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [
                {"icao24": "test1", "name": "Test 1", "_added_at": "2024-01-01"},
                {"icao24": "test2", "name": "Test 2", "_added_at": "2024-01-02"},
            ]

            with patch.object(handler, "_read_data", return_value=test_data):
                result = handler.get_all_aircrafts()

                # Проверяем что служебные поля удалены
                assert len(result) == 2
                assert "_added_at" not in result[0]
                assert "_added_at" not in result[1]
                assert result[0]["icao24"] == "test1"
                assert result[1]["icao24"] == "test2"

    def test_get_aircrafts_by_country(self, temp_dir):
        """Тест получения самолетов по стране."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [
                {"icao24": "test1", "origin_country": "USA", "name": "Test 1"},
                {"icao24": "test2", "origin_country": "Russia", "name": "Test 2"},
                {"icao24": "test3", "origin_country": "USA", "name": "Test 3"},
            ]

            with patch.object(handler, "_read_data", return_value=test_data):
                # Поиск без учета регистра
                result = handler.get_aircrafts_by_country("usa")
                assert len(result) == 2
                assert all(item["origin_country"] == "USA" for item in result)

                # Пустой результат
                result = handler.get_aircrafts_by_country("France")
                assert result == []

    def test_get_top_aircrafts_by_altitude(self, temp_dir):
        """Тест получения топ самолетов по высоте."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [
                {"icao24": "test1", "baro_altitude": 5000, "name": "Test 1"},
                {"icao24": "test2", "baro_altitude": 10000, "name": "Test 2"},
                {"icao24": "test3", "baro_altitude": 3000, "name": "Test 3"},
                {"icao24": "test4", "baro_altitude": 8000, "name": "Test 4"},
            ]

            with patch.object(handler, "_read_data", return_value=test_data):
                result = handler.get_top_aircrafts_by_altitude(2)

                assert len(result) == 2
                # Проверяем сортировку по убыванию высоты
                assert result[0]["baro_altitude"] == 10000
                assert result[1]["baro_altitude"] == 8000

    def test_delete_aircraft_success(self, temp_dir):
        """Тест успешного удаления самолета."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [
                {"icao24": "test1", "name": "Test 1"},
                {"icao24": "test2", "name": "Test 2"},
            ]

            with (
                patch.object(handler, "_read_data", return_value=test_data),
                patch.object(handler, "_write_data", return_value=True),
            ):

                result = handler.delete_aircraft("test1")
                assert result is True

    def test_delete_aircraft_not_found(self, temp_dir):
        """Тест удаления несуществующего самолета."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [
                {"icao24": "test1", "name": "Test 1"},
                {"icao24": "test2", "name": "Test 2"},
            ]

            with patch.object(handler, "_read_data", return_value=test_data):
                result = handler.delete_aircraft("test3")
                assert result is False

    def test_clear_all_data(self, temp_dir):
        """Тест очистки всех данных."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            with patch.object(handler, "_write_data", return_value=True):
                result = handler.clear_all_data()
                assert result is True

    def test_get_statistics_empty(self, temp_dir):
        """Тест получения статистики пустого файла."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            with patch.object(handler, "_read_data", return_value=[]):
                stats = handler.get_statistics()

                assert stats["total_aircrafts"] == 0
                assert stats["countries"] == {}
                assert "file_location" in stats

    def test_get_statistics_with_data(self, temp_dir):
        """Тест получения статистики с данными."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [
                {
                    "icao24": "test1",
                    "origin_country": "USA",
                    "baro_altitude": 10000,
                    "velocity": 250,
                },
                {
                    "icao24": "test2",
                    "origin_country": "USA",
                    "baro_altitude": 8000,
                    "velocity": 220,
                },
                {
                    "icao24": "test3",
                    "origin_country": "Russia",
                    "baro_altitude": 12000,
                    "velocity": 280,
                },
            ]

            with patch.object(handler, "_read_data", return_value=test_data):
                stats = handler.get_statistics()

                assert stats["total_aircrafts"] == 3
                assert stats["countries"]["USA"] == 2
                assert stats["countries"]["Russia"] == 1
                assert stats["altitude_stats"]["max"] == 12000
                assert stats["altitude_stats"]["min"] == 8000
                assert stats["speed_stats"]["max"] == 280
                assert stats["speed_stats"]["min"] == 220

    def test_get_aircraft_count(self, temp_dir):
        """Тест получения количества самолетов."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [{"icao24": "test1"}, {"icao24": "test2"}, {"icao24": "test3"}]

            with patch.object(handler, "_read_data", return_value=test_data):
                count = handler.get_aircraft_count()
                assert count == 3

    def test_get_countries(self, temp_dir):
        """Тест получения списка стран."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")
            handler.logger = Mock()

            test_data = [
                {"icao24": "test1", "origin_country": "USA"},
                {"icao24": "test2", "origin_country": "Russia"},
                {"icao24": "test3", "origin_country": "USA"},
                {"icao24": "test4", "origin_country": "Germany"},
            ]

            with patch.object(handler, "_read_data", return_value=test_data):
                countries = handler.get_countries()

                assert len(countries) == 3
                assert "USA" in countries
                assert "Russia" in countries
                assert "Germany" in countries
                # Проверяем сортировку
                assert countries == ["Germany", "Russia", "USA"]

    def test_get_file_path(self, temp_dir):
        """Тест получения пути к файлу."""
        with patch.object(Path, "cwd", return_value=temp_dir):
            handler = JSONFileHandler("test_data")

            expected_path = str(temp_dir / "data" / "test_data.json")
            assert handler.get_file_path() == expected_path

    def test_logger_initialization(self, temp_dir):
        """Тест инициализации логгера."""
        with (
            patch.object(Path, "cwd", return_value=temp_dir),
            patch("src.files.json_handler.loggers.create_logger") as mock_create_logger,
        ):

            mock_logger = Mock()
            mock_create_logger.return_value = mock_logger

            handler = JSONFileHandler("test_data")

            # Проверяем что логгер был создан
            mock_create_logger.assert_called_once()
            assert handler.logger == mock_logger


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
