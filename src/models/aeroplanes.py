"""
Модуль для работы с информацией о самолетах.
Содержит класс Aircraft для представления данных о воздушных судах.
"""

from dataclasses import dataclass, field
from functools import total_ordering
from typing import Any, List, Optional


@total_ordering
@dataclass(frozen=True, slots=True)
class Aircraft:
    """
    Класс для представления информации о воздушном судне.

    Использует frozen=True для неизменяемости и slots=True для оптимизации памяти.

    Атрибуты:
        icao24 (str): Уникальный идентификатор борта (ICAO24)
        callsign (str): Позывной рейса
        origin_country (str): Страна регистрации ВС
        longitude (float): Долгота в градусах
        latitude (float): Широта в градусах
        baro_altitude (float): Барометрическая высота в метрах
        velocity (float): Горизонтальная скорость в м/с
        true_track (float): Курс в градусах
        vertical_rate (float): Вертикальная скорость в м/с
        geo_altitude (float): Геометрическая высота в метрах
        on_ground (bool): Находится ли самолет на земле
        squawk (Optional[str]): Код ответчика транспондера
        spi (bool): Специальный сигнал (emergency/priority)
    """

    icao24: str
    callsign: str = field(default="UNKNOWN")
    origin_country: str = field(default="UNKNOWN")
    longitude: float = field(default=0.0)
    latitude: float = field(default=0.0)
    baro_altitude: float = field(default=0.0)
    velocity: float = field(default=0.0)
    true_track: float = field(default=0.0)
    vertical_rate: float = field(default=0.0)
    geo_altitude: float = field(default=0.0)
    on_ground: bool = field(default=False)
    squawk: Optional[str] = field(default=None)
    spi: bool = field(default=False)

    def __post_init__(self):
        """Выполняет валидацию после инициализации."""
        self._validate_and_set_fields()

    def _validate_and_set_fields(self) -> None:
        """Валидация и нормализация всех полей."""
        # Валидация icao24
        if not isinstance(self.icao24, str):
            raise ValueError(f"ICAO24 должен быть строкой, получен {type(self.icao24)}")

        icao24_cleaned = self.icao24.strip()
        if not icao24_cleaned:
            raise ValueError("ICAO24 не может быть пустой строкой")

        if len(icao24_cleaned) != 6 and icao24_cleaned != "UNKNOWN":
            raise ValueError(
                f"ICAO24 должен быть 6 символов, получено {len(icao24_cleaned)}"
            )

        # Используем object.__setattr__ для установки значений в frozen dataclass
        object.__setattr__(self, "icao24", icao24_cleaned)

        # Валидация остальных полей
        self._validate_string_field("callsign", allow_empty=True)
        self._validate_string_field("origin_country", allow_empty=False)

        self._validate_coordinates()
        self._validate_altitudes()
        self._validate_velocity()
        self._validate_track()
        self._validate_vertical_rate()
        self._validate_squawk()

    def _validate_string_field(self, field_name: str, allow_empty: bool = True) -> None:
        """Валидация строковых полей."""
        value = getattr(self, field_name)

        if value is None:
            default = "UNKNOWN" if allow_empty else "UNKNOWN"
            object.__setattr__(self, field_name, default)
        elif not isinstance(value, str):
            raise ValueError(f"{field_name} должен быть строкой, получен {type(value)}")
        else:
            cleaned = value.strip()
            if not cleaned and not allow_empty:
                raise ValueError(f"{field_name} не может быть пустой строкой")
            object.__setattr__(self, field_name, cleaned or "UNKNOWN")

    def _validate_coordinates(self) -> None:
        """Валидация координат."""
        # Валидация longitude
        if not isinstance(self.longitude, (int, float)):
            raise ValueError(
                f"Долгота должна быть числом, получен {type(self.longitude)}"
            )

        lon = float(self.longitude)
        if not (-180 <= lon <= 180):
            raise ValueError(f"Долгота должна быть от -180 до 180, получено {lon}")
        object.__setattr__(self, "longitude", lon)

        # Валидация latitude
        if not isinstance(self.latitude, (int, float)):
            raise ValueError(
                f"Широта должна быть числом, получен {type(self.latitude)}"
            )

        lat = float(self.latitude)
        if not (-90 <= lat <= 90):
            raise ValueError(f"Широта должна быть от -90 до 90, получено {lat}")
        object.__setattr__(self, "latitude", lat)

    def _validate_altitudes(self) -> None:
        """Валидация высот."""
        # Валидация baro_altitude
        if not isinstance(self.baro_altitude, (int, float)):
            raise ValueError(
                f"Барометрическая высота должна быть числом, получен {type(self.baro_altitude)}"
            )

        baro_alt = float(self.baro_altitude)
        if baro_alt < 0 or baro_alt > 20000:
            raise ValueError(f"Нереалистичная барометрическая высота: {baro_alt}м")
        object.__setattr__(self, "baro_altitude", baro_alt)

        # Валидация geo_altitude
        if not isinstance(self.geo_altitude, (int, float)):
            raise ValueError(
                f"Геометрическая высота должна быть числом, получен {type(self.geo_altitude)}"
            )

        geo_alt = float(self.geo_altitude)
        if geo_alt < 0 or geo_alt > 20000:
            raise ValueError(f"Нереалистичная геометрическая высота: {geo_alt}м")
        object.__setattr__(self, "geo_altitude", geo_alt)

    def _validate_velocity(self) -> None:
        """Валидация скорости."""
        if not isinstance(self.velocity, (int, float)):
            raise ValueError(
                f"Скорость должна быть числом, получен {type(self.velocity)}"
            )

        velocity_float = float(self.velocity)
        if velocity_float < 0 or velocity_float > 1000:
            raise ValueError(f"Нереалистичная скорость: {velocity_float} м/с")
        object.__setattr__(self, "velocity", velocity_float)

    def _validate_track(self) -> None:
        """Валидация курса."""
        if not isinstance(self.true_track, (int, float)):
            raise ValueError(
                f"Курс должен быть числом, получен {type(self.true_track)}"
            )

        track = float(self.true_track) % 360  # Нормализация к 0-360 градусам
        object.__setattr__(self, "true_track", track)

    def _validate_vertical_rate(self) -> None:
        """Валидация вертикальной скорости."""
        if not isinstance(self.vertical_rate, (int, float)):
            raise ValueError(
                f"Вертикальная скорость должна быть числом, получен {type(self.vertical_rate)}"
            )

        rate = float(self.vertical_rate)
        if abs(rate) > 100:
            raise ValueError(f"Нереалистичная вертикальная скорость: {rate} м/с")
        object.__setattr__(self, "vertical_rate", rate)

    def _validate_squawk(self) -> None:
        """Валидация кода ответчика."""
        if self.squawk is None:
            return

        if not isinstance(self.squawk, str):
            raise ValueError(f"Squawk должен быть строкой, получен {type(self.squawk)}")

        squawk_cleaned = self.squawk.strip()
        if not squawk_cleaned.isdigit() or len(squawk_cleaned) != 4:
            raise ValueError(
                f"Squawk должен быть 4 цифрами, получено '{squawk_cleaned}'"
            )

        object.__setattr__(self, "squawk", squawk_cleaned)

    # ========== СВОЙСТВА (PROPERTIES) ==========

    @property
    def velocity_kmh(self) -> float:
        """Скорость в км/ч."""
        return self.velocity * 3.6

    @property
    def altitude_feet(self) -> float:
        """Высота в футах."""
        return self.baro_altitude * 3.28084

    # ========== МЕТОДЫ СРАВНЕНИЯ (total_ordering) ==========

    def __eq__(self, other: Any) -> bool:
        """Проверка равенства по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return abs(self.baro_altitude - other.baro_altitude) < 0.1

    def __lt__(self, other: Any) -> bool:
        """Сравнение: меньше по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.baro_altitude < other.baro_altitude

    # ========== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ==========

    def is_climbing(self) -> bool:
        """Проверяет, набирает ли самолет высоту."""
        return self.vertical_rate > 1.0

    def is_descending(self) -> bool:
        """Проверяет, снижается ли самолет."""
        return self.vertical_rate < -1.0

    def is_level(self) -> bool:
        """Проверяет, летит ли самолет горизонтально."""
        return abs(self.vertical_rate) <= 1.0

    def get_speed_category(self) -> str:
        """Определяет категорию скорости."""
        speed_kmh = self.velocity_kmh
        if speed_kmh < 100:
            return "Медленно"
        elif speed_kmh < 300:
            return "Крейсерская"
        elif speed_kmh < 500:
            return "Быстро"
        else:
            return "Очень быстро"

    def get_altitude_category(self) -> str:
        """Определяет категорию высоты."""
        altitude_feet = self.altitude_feet
        if altitude_feet < 10000:
            return "Низкая"
        elif altitude_feet < 20000:
            return "Средняя"
        elif altitude_feet < 30000:
            return "Высокая"
        else:
            return "Очень высокая"

    def to_dict(self) -> dict:
        """Преобразует объект в словарь."""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "baro_altitude": self.baro_altitude,
            "velocity": self.velocity,
            "true_track": self.true_track,
            "vertical_rate": self.vertical_rate,
            "geo_altitude": self.geo_altitude,
            "on_ground": self.on_ground,
            "squawk": self.squawk,
            "spi": self.spi,
        }

    @classmethod
    def from_opensky_data(cls, data: List[Any]) -> "Aircraft":
        """
        Создает объект Aircraft из данных OpenSky Network.

        Args:
            data (List[Any]): Список данных в формате OpenSky

        Returns:
            Aircraft: Объект самолета

        Raises:
            ValueError: При невалидных данных
        """
        if len(data) < 17:
            raise ValueError(
                f"Недостаточно данных для создания Aircraft: {len(data)} элементов"
            )

        return cls(
            icao24=data[0],
            callsign=data[1],
            origin_country=data[2],
            longitude=data[5],
            latitude=data[6],
            baro_altitude=data[7],
            velocity=data[9],
            true_track=data[10],
            vertical_rate=data[11],
            geo_altitude=data[13],
            on_ground=data[8],
            squawk=data[14],
            spi=data[15],
        )

    def __str__(self) -> str:
        """Строковое представление самолета."""
        if self.on_ground:
            status = "НА ЗЕМЛЕ"
        else:
            status = f"В ВОЗДУХЕ ({self.altitude_feet:.0f} футов)"

        return (
            f"Рейс {self.callsign} ({self.icao24}) - {self.origin_country}\n"
            f"Положение: {self.latitude:.4f}°N, {self.longitude:.4f}°E\n"
            f"Статус: {status}, Скорость: {self.velocity_kmh:.0f} км/ч\n"
            f"Курс: {self.true_track:.0f}°, "
            f"Верт. скорость: {self.vertical_rate:.1f} м/с"
        )
