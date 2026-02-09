"""
Чистые тесты для класса Aircraft без сохранения файлов.
"""

import pytest

from src.models.aeroplanes import Aircraft


class TestAircraftBasic:
    """Тесты базовой функциональности Aircraft."""

    def test_create_minimal(self):
        """Тест создания самолета с минимальными данными."""
        plane = Aircraft(icao24="A0B1C2")  # 6 символов!

        assert plane.icao24 == "A0B1C2"
        assert plane.callsign == "UNKNOWN"
        assert plane.origin_country == "UNKNOWN"
        assert plane.baro_altitude == 0.0

    def test_create_full(self):
        """Тест создания самолета со всеми полями."""
        plane = Aircraft(
            icao24="D3E4F5",  # 6 символов!
            callsign="BA456",
            origin_country="UK",
            longitude=37.6173,
            latitude=55.7558,
            baro_altitude=10000.0,
        )

        assert plane.icao24 == "D3E4F5"
        assert plane.callsign == "BA456"
        assert plane.origin_country == "UK"
        assert plane.longitude == 37.6173
        assert plane.latitude == 55.7558
        assert plane.baro_altitude == 10000.0


class TestAircraftValidation:
    """Тесты валидации данных."""

    def test_invalid_icao24_length(self):
        """Тест некорректной длины ICAO24."""
        with pytest.raises(ValueError, match="ICAO24 должен быть 6 символов"):
            Aircraft(icao24="ABC")  # 3 символа

    def test_empty_icao24(self):
        """Тест пустого ICAO24."""
        with pytest.raises(ValueError, match="ICAO24 не может быть пустой строкой"):
            Aircraft(icao24="   ")

    def test_valid_icao24_unknown(self):
        """Тест специального значения UNKNOWN."""
        # UNKNOWN должно быть разрешено
        plane = Aircraft(icao24="UNKNOWN")
        assert plane.icao24 == "UNKNOWN"

    def test_invalid_coordinates(self):
        """Тест некорректных координат."""
        # Долгота вне диапазона
        with pytest.raises(ValueError, match="Долгота должна быть от -180 до 180"):
            Aircraft(icao24="A0B1C2", longitude=200.0)

        # Широта вне диапазона
        with pytest.raises(ValueError, match="Широта должна быть от -90 до 90"):
            Aircraft(icao24="A0B1C2", latitude=100.0)

    def test_invalid_altitude(self):
        """Тест некорректной высоты."""
        with pytest.raises(ValueError, match="Нереалистичная барометрическая высота"):
            Aircraft(icao24="A0B1C2", baro_altitude=50000.0)

    def test_invalid_squawk(self):
        """Тест некорректного squawk."""
        with pytest.raises(ValueError, match="Squawk должен быть 4 цифрами"):
            Aircraft(icao24="A0B1C2", squawk="123")


class TestAircraftComparison:
    """Тесты сравнения самолетов."""

    def test_height_comparison(self):
        """Тест сравнения по высоте."""
        plane_low = Aircraft(icao24="A0B1C2", baro_altitude=10000.0)
        plane_high = Aircraft(icao24="D3E4F5", baro_altitude=12000.0)
        plane_same = Aircraft(icao24="G7H8I9", baro_altitude=10000.0)

        # Меньше
        assert plane_low < plane_high
        assert not plane_high < plane_low

        # Больше
        assert plane_high > plane_low
        assert not plane_low > plane_high

        # Равно (с учетом погрешности)
        assert plane_low == plane_same
        assert not plane_low == plane_high

        # Не равно
        assert plane_low != plane_high
        assert not plane_low != plane_same

    def test_comparison_with_other_types(self):
        """Тест сравнения с другими типами."""
        plane = Aircraft(icao24="A0B1C2")

        # Сравнение с не-Aircraft объектом должно возвращать NotImplemented
        assert plane.__eq__("not a plane") == NotImplemented
        assert plane.__lt__("not a plane") == NotImplemented


class TestAircraftProperties:
    """Тесты свойств самолета."""

    def test_velocity_kmh(self):
        """Тест преобразования скорости в км/ч."""
        plane = Aircraft(icao24="A0B1C2", velocity=100.0)
        assert plane.velocity_kmh == 360.0  # 100 * 3.6

    def test_altitude_feet(self):
        """Тест преобразования высоты в футы."""
        plane = Aircraft(icao24="A0B1C2", baro_altitude=3048.0)  # 10000 футов
        assert plane.altitude_feet == pytest.approx(10000.0, rel=0.01)


class TestAircraftMethods:
    """Тесты методов самолета."""

    def test_climbing_descending(self):
        """Тест определения набора/снижения высоты."""
        # Набор высоты
        climbing = Aircraft(icao24="A0B1C2", vertical_rate=5.0)
        assert climbing.is_climbing() is True
        assert climbing.is_descending() is False
        assert climbing.is_level() is False

        # Снижение
        descending = Aircraft(icao24="D3E4F5", vertical_rate=-3.0)
        assert descending.is_climbing() is False
        assert descending.is_descending() is True
        assert descending.is_level() is False

        # Горизонтальный полет
        level = Aircraft(icao24="G7H8I9", vertical_rate=0.5)
        assert level.is_climbing() is False
        assert level.is_descending() is False
        assert level.is_level() is True

    def test_speed_category(self):
        """Тест категорий скорости."""
        test_cases = [
            (20.0, "Медленно"),  # 72 км/ч
            (80.0, "Крейсерская"),  # 288 км/ч
            (120.0, "Быстро"),  # 432 км/ч
            (150.0, "Очень быстро"),  # 540 км/ч
        ]

        # Используем разные 6-символьные ICAO24 для каждого теста
        icao24_list = ["A0B1C2", "D3E4F5", "G7H8I9", "J0K1L2"]

        for (speed, expected), icao24 in zip(test_cases, icao24_list):
            plane = Aircraft(icao24=icao24, velocity=speed)  # 6 символов!
            assert plane.get_speed_category() == expected

    def test_altitude_category(self):
        """Тест категорий высоты."""
        test_cases = [
            (2000.0, "Низкая"),  # ~6562 футов
            (6000.0, "Средняя"),  # ~19685 футов
            (9000.0, "Высокая"),  # ~29528 футов
            (11000.0, "Очень высокая"),  # ~36089 футов
        ]

        # Используем разные 6-символьные ICAO24 для каждого теста
        icao24_list = ["A0B1C2", "D3E4F5", "G7H8I9", "J0K1L2"]

        for (altitude, expected), icao24 in zip(test_cases, icao24_list):
            plane = Aircraft(icao24=icao24, baro_altitude=altitude)  # 6 символов!
            assert plane.get_altitude_category() == expected


class TestAircraftSerialization:
    """Тесты сериализации."""

    def test_to_dict(self):
        """Тест преобразования в словарь."""
        plane = Aircraft(
            icao24="A0B1C2",  # 6 символов!
            callsign="SU123",
            origin_country="Russia",
            baro_altitude=10000.0,
        )

        data = plane.to_dict()

        assert isinstance(data, dict)
        assert data["icao24"] == "A0B1C2"
        assert data["callsign"] == "SU123"
        assert data["origin_country"] == "Russia"
        assert data["baro_altitude"] == 10000.0
        # Проверяем что все нужные поля есть
        expected_keys = {
            "icao24",
            "callsign",
            "origin_country",
            "longitude",
            "latitude",
            "baro_altitude",
            "velocity",
            "true_track",
            "vertical_rate",
            "geo_altitude",
            "on_ground",
            "squawk",
            "spi",
        }
        assert set(data.keys()) == expected_keys

    def test_from_opensky_data(self):
        """Тест создания из данных OpenSky."""
        opensky_data = [
            "A0B1C2",  # icao24
            "SU123",  # callsign
            "Russia",  # origin_country
            None,
            None,  # time_position, last_contact
            37.6173,  # longitude
            55.7558,  # latitude
            10000.0,  # baro_altitude
            False,  # on_ground
            250.0,  # velocity
            180.0,  # true_track
            5.0,  # vertical_rate
            None,  # sensors
            10500.0,  # geo_altitude
            "7700",  # squawk
            False,  # spi
            None,  # position_source
        ]

        plane = Aircraft.from_opensky_data(opensky_data)

        assert plane.icao24 == "A0B1C2"
        assert plane.callsign == "SU123"
        assert plane.origin_country == "Russia"
        assert plane.longitude == 37.6173
        assert plane.latitude == 55.7558
        assert plane.baro_altitude == 10000.0
        assert plane.velocity == 250.0

    def test_from_opensky_invalid(self):
        """Тест создания из неполных данных OpenSky."""
        with pytest.raises(ValueError, match="Недостаточно данных"):
            Aircraft.from_opensky_data(["A0B1C2", "SU123"])


class TestAircraftStringRepresentation:
    """Тесты строкового представления."""

    def test_str_airborne(self):
        """Тест строкового представления самолета в воздухе."""
        plane = Aircraft(
            icao24="A0B1C2",  # 6 символов!
            callsign="SU123",
            origin_country="Russia",
            latitude=55.7558,
            longitude=37.6173,
            baro_altitude=10000.0,
            velocity=250.0,
            true_track=180.0,
            vertical_rate=5.0,
            on_ground=False,
        )

        text = str(plane)

        assert "Рейс SU123 (A0B1C2) - Russia" in text
        assert "Положение: 55.7558°N, 37.6173°E" in text
        assert "В ВОЗДУХЕ" in text
        assert "900 км/ч" in text  # 250 * 3.6 = 900
        assert "Курс: 180°" in text

    def test_str_on_ground(self):
        """Тест строкового представления самолета на земле."""
        plane = Aircraft(
            icao24="D3E4F5",  # 6 символов!
            callsign="BA456",
            origin_country="UK",
            on_ground=True,
        )

        text = str(plane)
        assert "НА ЗЕМЛЕ" in text


def test_frozen_dataclass():
    """Тест что dataclass действительно frozen (неизменяемый)."""
    plane = Aircraft(icao24="A0B1C2")  # 6 символов!

    # Не должно быть возможности изменять атрибуты
    with pytest.raises(AttributeError):
        plane.icao24 = "NEW123"

    with pytest.raises(AttributeError):
        plane.callsign = "NEWCALL"
