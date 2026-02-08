"""
Тесты для модуля aeroplanes (класс Aircraft).
"""

import unittest
from typing import Any, List

from src.models.aeroplanes import Aircraft


class TestAircraftCreation(unittest.TestCase):
    """Тесты создания объектов Aircraft."""

    def test_create_valid_aircraft(self):
        """Тест создания валидного самолета."""
        plane = Aircraft(
            icao24="abcdef",
            callsign="TEST01",
            origin_country="Testland",
            longitude=10.0,
            latitude=20.0,
            baro_altitude=10000.0,
            velocity=250.0,
            true_track=180.0,
            vertical_rate=5.0,
            geo_altitude=10100.0,
            on_ground=False,
            squawk="1234",
            spi=False,
        )

        self.assertEqual(plane.icao24, "abcdef")
        self.assertEqual(plane.callsign, "TEST01")
        self.assertEqual(plane.origin_country, "Testland")
        self.assertEqual(plane.baro_altitude, 10000.0)
        self.assertEqual(plane.velocity, 250.0)
        self.assertFalse(plane.on_ground)
        self.assertEqual(plane.squawk, "1234")
        self.assertFalse(plane.spi)

    def test_create_with_minimal_data(self):
        """Тест создания с минимальными данными."""
        plane = Aircraft(
            icao24="123456",
            callsign="MINI01",
            origin_country="Miniland",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=5000.0,
            velocity=200.0,
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=5000.0,
            on_ground=True,
        )

        self.assertEqual(plane.icao24, "123456")
        self.assertTrue(plane.on_ground)
        self.assertIsNone(plane.squawk)
        self.assertFalse(plane.spi)

    def test_create_with_none_values(self):
        """Тест создания с None значениями."""
        plane = Aircraft(
            icao24="none12",  # Должен быть 6 символов!
            callsign=None,  # Будет преобразовано в "UNKNOWN"
            origin_country=None,  # Будет преобразовано в "UNKNOWN"
            longitude=None,  # Будет преобразовано в 0.0
            latitude=None,  # Будет преобразовано в 0.0
            baro_altitude=None,  # Будет преобразовано в 0.0
            velocity=None,  # Будет преобразовано в 0.0
            true_track=None,  # Будет преобразовано в 0.0
            vertical_rate=None,  # Будет преобразовано в 0.0
            geo_altitude=None,  # Будет преобразовано в 0.0
            on_ground=False,
        )

        self.assertEqual(plane.icao24, "none12")
        self.assertEqual(plane.callsign, "UNKNOWN")
        self.assertEqual(plane.origin_country, "UNKNOWN")
        self.assertEqual(plane.longitude, 0.0)
        self.assertEqual(plane.latitude, 0.0)
        self.assertEqual(plane.baro_altitude, 0.0)
        self.assertEqual(plane.velocity, 0.0)
        self.assertEqual(plane.true_track, 0.0)
        self.assertEqual(plane.vertical_rate, 0.0)
        self.assertEqual(plane.geo_altitude, 0.0)


class TestAircraftValidation(unittest.TestCase):
    """Тесты валидации данных в классе Aircraft."""

    def test_invalid_icao24_too_short(self):
        """Тест с некорректным ICAO24 (слишком короткий)."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abc",  # Слишком короткий
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=1000.0,
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
            )
        self.assertIn("ICAO24 должен быть 6 символов", str(context.exception))

    def test_invalid_icao24_empty(self):
        """Тест с пустым ICAO24."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="   ",  # Пустая строка после очистки
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=1000.0,
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
            )
        self.assertIn("ICAO24 не может быть пустой строкой", str(context.exception))

    def test_invalid_coordinates_longitude(self):
        """Тест с некорректной долготой."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=200.0,  # Невалидная долгота (> 180)
                latitude=0.0,
                baro_altitude=1000.0,
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
            )
        self.assertIn("Долгота должна быть от -180 до 180", str(context.exception))

    def test_invalid_coordinates_latitude(self):
        """Тест с некорректной широтой."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=100.0,  # Невалидная широта (> 90)
                baro_altitude=1000.0,
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
            )
        self.assertIn("Широта должна быть от -90 до 90", str(context.exception))

    def test_invalid_altitude_too_high(self):
        """Тест с нереалистичной высотой."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=50000.0,  # Слишком высоко
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=50000.0,
                on_ground=False,
            )
        self.assertIn("Нереалистичная барометрическая высота", str(context.exception))

    def test_invalid_altitude_negative(self):
        """Тест с отрицательной высотой."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=-100.0,  # Отрицательная высота
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=-100.0,
                on_ground=False,
            )
        self.assertIn("Нереалистичная барометрическая высота", str(context.exception))

    def test_invalid_velocity_too_fast(self):
        """Тест с нереалистичной скоростью."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=1000.0,
                velocity=1500.0,  # Слишком быстро (> 1000 м/с)
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
            )
        self.assertIn("Нереалистичная скорость", str(context.exception))

    def test_invalid_velocity_negative(self):
        """Тест с отрицательной скоростью."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=1000.0,
                velocity=-100.0,  # Отрицательная скорость
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
            )
        self.assertIn("Нереалистичная скорость", str(context.exception))

    def test_invalid_squawk_not_digits(self):
        """Тест с некорректным squawk (не цифры)."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=1000.0,
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
                squawk="12ab",  # Не только цифры
            )
        self.assertIn("Squawk должен быть 4 цифрами", str(context.exception))

    def test_invalid_squawk_wrong_length(self):
        """Тест с некорректным squawk (неправильная длина)."""
        with self.assertRaises(ValueError) as context:
            Aircraft(
                icao24="abcdef",
                callsign="TEST",
                origin_country="Test",
                longitude=0.0,
                latitude=0.0,
                baro_altitude=1000.0,
                velocity=200.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=1000.0,
                on_ground=False,
                squawk="123",  # Слишком короткий
            )
        self.assertIn("Squawk должен быть 4 цифрами", str(context.exception))


class TestAircraftProperties(unittest.TestCase):
    """Тесты свойств Aircraft."""

    def setUp(self):
        """Настройка тестового самолета."""
        self.plane = Aircraft(
            icao24="test12",  # 6 символов!
            callsign="PROP01",
            origin_country="Propland",
            longitude=30.0,
            latitude=40.0,
            baro_altitude=10000.0,
            velocity=250.0,  # 900 км/ч
            true_track=90.0,
            vertical_rate=10.0,
            geo_altitude=10200.0,
            on_ground=False,
            squawk="7700",  # Аварийный код
            spi=True,
        )

    def test_velocity_conversion(self):
        """Тест конвертации скорости в км/ч."""
        # 250 м/с = 900 км/ч
        self.assertAlmostEqual(self.plane.velocity_kmh, 900.0, places=1)

    def test_altitude_conversion(self):
        """Тест конвертации высоты в футы."""
        # 10000 м ≈ 32808.4 футов
        self.assertAlmostEqual(self.plane.altitude_feet, 32808.4, places=1)

    def test_climbing_status(self):
        """Тест определения набора высоты."""
        self.assertTrue(self.plane.is_climbing())  # vertical_rate = 10.0
        self.assertFalse(self.plane.is_descending())
        self.assertFalse(self.plane.is_level())

    def test_descending_status(self):
        """Тест определения снижения."""
        descending_plane = Aircraft(
            icao24="desc12",  # 6 символов!
            callsign="DESC01",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=5000.0,
            velocity=200.0,
            true_track=0.0,
            vertical_rate=-5.0,  # Отрицательная скорость
            geo_altitude=5000.0,
            on_ground=False,
        )

        self.assertTrue(descending_plane.is_descending())
        self.assertFalse(descending_plane.is_climbing())
        self.assertFalse(descending_plane.is_level())

    def test_level_status(self):
        """Тест определения горизонтального полета."""
        level_plane = Aircraft(
            icao24="level1",  # 6 символов!
            callsign="LEVEL01",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=5000.0,
            velocity=200.0,
            true_track=0.0,
            vertical_rate=0.5,  # Маленькая скорость
            geo_altitude=5000.0,
            on_ground=False,
        )

        self.assertTrue(level_plane.is_level())
        self.assertFalse(level_plane.is_climbing())
        self.assertFalse(level_plane.is_descending())

    def test_speed_category(self):
        """Тест категорий скорости."""
        # 900 км/ч = "Очень быстро" (>= 500 км/ч)
        self.assertEqual(self.plane.get_speed_category(), "Очень быстро")

        # Проверка других категорий
        slow_plane = Aircraft(
            icao24="slow12",  # 6 символов!
            callsign="SLOW01",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=1000.0,
            velocity=20.0,  # 72 км/ч (< 100)
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=1000.0,
            on_ground=False,
        )
        self.assertEqual(slow_plane.get_speed_category(), "Медленно")

        # Крейсерская скорость (100-300 км/ч)
        cruise_plane = Aircraft(
            icao24="cruis1",  # 6 символов!
            callsign="CRUISE",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=5000.0,
            velocity=80.0,  # 288 км/ч
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=5000.0,
            on_ground=False,
        )
        self.assertEqual(cruise_plane.get_speed_category(), "Крейсерская")

        # Быстрая скорость (300-500 км/ч)
        fast_plane = Aircraft(
            icao24="fast12",  # 6 символов!
            callsign="FAST01",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=5000.0,
            velocity=120.0,  # 432 км/ч
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=5000.0,
            on_ground=False,
        )
        self.assertEqual(fast_plane.get_speed_category(), "Быстро")


class TestAircraftComparison(unittest.TestCase):
    """Тесты сравнения самолетов."""

    def setUp(self):
        """Настройка тестовых самолетов."""
        self.plane_low = Aircraft(
            icao24="low123",  # 6 символов!
            callsign="LOW001",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=1000.0,
            velocity=200.0,
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=1000.0,
            on_ground=False,
        )

        self.plane_high = Aircraft(
            icao24="high45",  # 6 символов!
            callsign="HIGH01",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=10000.0,
            velocity=200.0,
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=10000.0,
            on_ground=False,
        )

    def test_less_than(self):
        """Тест оператора < (меньше)."""
        self.assertTrue(self.plane_low < self.plane_high)
        self.assertFalse(self.plane_high < self.plane_low)

    def test_greater_than(self):
        """Тест оператора > (больше)."""
        self.assertTrue(self.plane_high > self.plane_low)
        self.assertFalse(self.plane_low > self.plane_high)

    def test_less_than_or_equal(self):
        """Тест оператора <= (меньше или равно)."""
        self.assertTrue(self.plane_low <= self.plane_high)
        self.assertTrue(self.plane_low <= self.plane_low)  # Равны себе
        self.assertFalse(self.plane_high <= self.plane_low)

    def test_greater_than_or_equal(self):
        """Тест оператора >= (больше или равно)."""
        self.assertTrue(self.plane_high >= self.plane_low)
        self.assertTrue(self.plane_high >= self.plane_high)  # Равны себе
        self.assertFalse(self.plane_low >= self.plane_high)

    def test_equal(self):
        """Тест оператора == (равно)."""
        # Разные самолеты с разной высотой
        self.assertFalse(self.plane_low == self.plane_high)

        # Один и тот же самолет
        self.assertTrue(self.plane_low == self.plane_low)

        # Два самолета с одинаковой высотой
        plane_same = Aircraft(
            icao24="same67",  # 6 символов!
            callsign="SAME01",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=1000.0,  # Такая же высота
            velocity=200.0,
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=1000.0,
            on_ground=False,
        )
        self.assertTrue(self.plane_low == plane_same)

    def test_not_equal(self):
        """Тест оператора != (не равно)."""
        self.assertTrue(self.plane_low != self.plane_high)
        self.assertFalse(self.plane_low != self.plane_low)

    def test_comparison_with_other_types(self):
        """Тест сравнения с другими типами."""
        # Сравнение с не-Aircraft объектом должно возвращать NotImplemented
        self.assertEqual(self.plane_low.__eq__("not an aircraft"), NotImplemented)
        self.assertEqual(self.plane_low.__lt__(123), NotImplemented)
        self.assertEqual(self.plane_low.__gt__([1, 2, 3]), NotImplemented)


class TestAircraftFromOpensky(unittest.TestCase):
    """Тесты создания из данных OpenSky."""

    def test_from_opensky_valid(self):
        """Тест создания из валидных данных OpenSky."""
        opensky_data: List[Any] = [
            "4b1812",  # 0: icao24
            "SWR438A ",  # 1: callsign
            "Switzerland",  # 2: origin_country
            1766166618,  # 3: time_position
            1766166618,  # 4: last_contact
            -0.0168,  # 5: longitude
            51.0888,  # 6: latitude
            4267.2,  # 7: baro_altitude
            False,  # 8: on_ground
            189.7,  # 9: velocity
            129.39,  # 10: true_track
            14.63,  # 11: vertical_rate
            None,  # 12: sensors
            4282.44,  # 13: geo_altitude
            "2061",  # 14: squawk
            False,  # 15: spi
            0,  # 16: position_source
        ]

        plane = Aircraft.from_opensky_data(opensky_data)

        self.assertEqual(plane.icao24, "4b1812")
        self.assertEqual(plane.callsign, "SWR438A")
        self.assertEqual(plane.origin_country, "Switzerland")
        self.assertAlmostEqual(plane.longitude, -0.0168)
        self.assertAlmostEqual(plane.latitude, 51.0888)
        self.assertAlmostEqual(plane.baro_altitude, 4267.2)
        self.assertAlmostEqual(plane.velocity, 189.7)
        self.assertAlmostEqual(plane.true_track, 129.39)
        self.assertAlmostEqual(plane.vertical_rate, 14.63)
        self.assertAlmostEqual(plane.geo_altitude, 4282.44)
        self.assertFalse(plane.on_ground)
        self.assertEqual(plane.squawk, "2061")
        self.assertFalse(plane.spi)

    def test_from_opensky_invalid(self):
        """Тест с неполными данными OpenSky."""
        with self.assertRaises(ValueError) as context:
            Aircraft.from_opensky_data(["only", "two", "items"])

        self.assertIn("Недостаточно данных", str(context.exception))

    def test_from_opensky_empty_list(self):
        """Тест с пустым списком."""
        with self.assertRaises(ValueError) as context:
            Aircraft.from_opensky_data([])

        self.assertIn("Недостаточно данных", str(context.exception))


class TestAircraftMethods(unittest.TestCase):
    """Тесты методов Aircraft."""

    def setUp(self):
        """Настройка тестового самолета."""
        self.plane = Aircraft(
            icao24="dict12",  # 6 символов!
            callsign="DICT01",
            origin_country="Dictland",
            longitude=10.0,
            latitude=20.0,
            baro_altitude=5000.0,
            velocity=200.0,
            true_track=45.0,
            vertical_rate=2.5,
            geo_altitude=5100.0,
            on_ground=False,
            squawk="4321",
            spi=True,
        )

    def test_to_dict(self):
        """Тест преобразования в словарь."""
        data = self.plane.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["icao24"], "dict12")
        self.assertEqual(data["callsign"], "DICT01")
        self.assertEqual(data["origin_country"], "Dictland")
        self.assertEqual(data["longitude"], 10.0)
        self.assertEqual(data["latitude"], 20.0)
        self.assertEqual(data["baro_altitude"], 5000.0)
        self.assertEqual(data["velocity"], 200.0)
        self.assertEqual(data["true_track"], 45.0)
        self.assertEqual(data["vertical_rate"], 2.5)
        self.assertEqual(data["geo_altitude"], 5100.0)
        self.assertEqual(data["on_ground"], False)
        self.assertEqual(data["squawk"], "4321")
        self.assertEqual(data["spi"], True)

        # Проверка что все поля присутствуют
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
        self.assertEqual(set(data.keys()), expected_keys)

    def test_str_representation(self):
        """Тест строкового представления."""
        result = str(self.plane)

        # Проверка наличия ключевой информации
        self.assertIn("DICT01", result)
        self.assertIn("dict12", result)
        self.assertIn("Dictland", result)
        self.assertIn("В ВОЗДУХЕ", result)  # on_ground=False
        self.assertIn("футов", result)  # Высота в футах
        self.assertIn("км/ч", result)  # Скорость в км/ч

        # Тест для самолета на земле
        ground_plane = Aircraft(
            icao24="ground",  # 6 символов!
            callsign="GROUND",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            velocity=0.0,
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=0.0,
            on_ground=True,
        )

        ground_str = str(ground_plane)
        self.assertIn("НА ЗЕМЛЕ", ground_str)
        self.assertNotIn("футов", ground_str)

    def test_repr_representation(self):
        """Тест технического строкового представления."""
        result = repr(self.plane)

        self.assertIn("Aircraft", result)
        self.assertIn("dict12", result)
        self.assertIn("DICT01", result)
        self.assertIn("Dictland", result)
        self.assertIn("altitude=5000.0m", result)

    def test_slots_attribute(self):
        """Тест что класс использует __slots__."""
        self.assertTrue(hasattr(Aircraft, "__slots__"))

        # Проверка что нельзя добавить новый атрибут
        with self.assertRaises(AttributeError):
            self.plane.new_attribute = "test"  # type: ignore

        # Проверка что можно изменить существующий атрибут через свойства
        # (но только через внутренние методы валидации)

    def test_properties_read_only(self):
        """Тест что свойства только для чтения."""
        # Нельзя изменить свойства напрямую
        with self.assertRaises(AttributeError):
            self.plane.icao24 = "new_value"  # type: ignore

        with self.assertRaises(AttributeError):
            self.plane.callsign = "new_call"  # type: ignore

        with self.assertRaises(AttributeError):
            self.plane.baro_altitude = 10000.0  # type: ignore


class TestAircraftEdgeCases(unittest.TestCase):
    """Тесты граничных случаев для Aircraft."""

    def test_track_normalization(self):
        """Тест нормализации курса (0-360 градусов)."""
        # Курс больше 360 градусов
        plane1 = Aircraft(
            icao24="track1",  # 6 символов!
            callsign="TRACK1",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=1000.0,
            velocity=200.0,
            true_track=450.0,  # 450 - 360 = 90
            vertical_rate=0.0,
            geo_altitude=1000.0,
            on_ground=False,
        )
        self.assertAlmostEqual(plane1.true_track, 90.0)

        # Курс отрицательный
        plane2 = Aircraft(
            icao24="track2",  # 6 символов!
            callsign="TRACK2",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=1000.0,
            velocity=200.0,
            true_track=-90.0,  # -90 + 360 = 270
            vertical_rate=0.0,
            geo_altitude=1000.0,
            on_ground=False,
        )
        self.assertAlmostEqual(plane2.true_track, 270.0)

        # Курс ровно 360
        plane3 = Aircraft(
            icao24="track3",  # 6 символов!
            callsign="TRACK3",
            origin_country="Test",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=1000.0,
            velocity=200.0,
            true_track=360.0,
            vertical_rate=0.0,
            geo_altitude=1000.0,
            on_ground=False,
        )
        self.assertAlmostEqual(plane3.true_track, 0.0)

    def test_whitespace_handling(self):
        """Тест обработки пробелов в строках."""
        plane = Aircraft(
            icao24="  abcdef  ",  # 6 символов после очистки
            callsign="  TEST01  ",
            origin_country="  Testland  ",
            longitude=0.0,
            latitude=0.0,
            baro_altitude=1000.0,
            velocity=200.0,
            true_track=0.0,
            vertical_rate=0.0,
            geo_altitude=1000.0,
            on_ground=False,
            squawk="  1234  ",
        )

        # Пробелы должны быть удалены
        self.assertEqual(plane.icao24, "abcdef")
        self.assertEqual(plane.callsign, "TEST01")
        self.assertEqual(plane.origin_country, "Testland")
        self.assertEqual(plane.squawk, "1234")

    def test_very_small_values(self):
        """Тест очень маленьких значений."""
        plane = Aircraft(
            icao24="small1",  # 6 символов!
            callsign="SMALL01",
            origin_country="Test",
            longitude=0.000001,
            latitude=-0.000001,
            baro_altitude=0.1,  # Очень низко
            velocity=0.1,  # Очень медленно
            true_track=0.001,
            vertical_rate=0.001,
            geo_altitude=0.1,
            on_ground=False,
        )

        self.assertAlmostEqual(plane.longitude, 0.000001)
        self.assertAlmostEqual(plane.latitude, -0.000001)
        self.assertAlmostEqual(plane.baro_altitude, 0.1)
        self.assertAlmostEqual(plane.velocity, 0.1)
        self.assertAlmostEqual(plane.true_track, 0.001)
        self.assertAlmostEqual(plane.vertical_rate, 0.001)

    def test_maximum_valid_values(self):
        """Тест максимально допустимых значений."""
        plane = Aircraft(
            icao24="maxval",  # 6 символов!
            callsign="MAXVAL",
            origin_country="Test",
            longitude=180.0,  # Максимальная долгота
            latitude=90.0,  # Максимальная широта
            baro_altitude=20000.0,  # Максимальная высота
            velocity=1000.0,  # Максимальная скорость
            true_track=359.999,
            vertical_rate=100.0,  # Максимальная вертикальная скорость
            geo_altitude=20000.0,
            on_ground=False,
        )

        self.assertEqual(plane.longitude, 180.0)
        self.assertEqual(plane.latitude, 90.0)
        self.assertEqual(plane.baro_altitude, 20000.0)
        self.assertEqual(plane.velocity, 1000.0)
        self.assertAlmostEqual(plane.true_track, 359.999)
        self.assertEqual(plane.vertical_rate, 100.0)

        # Проверка конвертаций
        self.assertAlmostEqual(plane.velocity_kmh, 3600.0, places=1)
        self.assertAlmostEqual(plane.altitude_feet, 65616.8, places=1)
