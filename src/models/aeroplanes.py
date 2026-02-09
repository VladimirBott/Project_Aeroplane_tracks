"""
Модуль для работы с информацией о самолетах.
Содержит класс Aircraft для представления данных о воздушных судах.
"""

from typing import Any, List, Optional


class Aircraft:
    """
    Класс для представления информации о воздушном судне.

    Использует __slots__ для экономии памяти и повышения производительности.
    Реализует методы сравнения самолетов по высоте полета.

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
    """

    __slots__ = (
        "_icao24",
        "_callsign",
        "_origin_country",
        "_longitude",
        "_latitude",
        "_baro_altitude",
        "_velocity",
        "_true_track",
        "_vertical_rate",
        "_geo_altitude",
        "_on_ground",
        "_squawk",
        "_spi",
    )

    def __init__(
        self,
        icao24: str,
        callsign: Optional[str],
        origin_country: Optional[str],
        longitude: Optional[float],
        latitude: Optional[float],
        baro_altitude: Optional[float],
        velocity: Optional[float],
        true_track: Optional[float],
        vertical_rate: Optional[float],
        geo_altitude: Optional[float],
        on_ground: Optional[bool],
        squawk: Optional[str] = None,
        spi: Optional[bool] = False,
    ) -> None:
        """
        Инициализация объекта самолета.

        Args:
            icao24 (str): Уникальный идентификатор борта (ICAO24)
            callsign (Optional[str]): Позывной рейса
            origin_country (Optional[str]): Страна регистрации ВС
            longitude (Optional[float]): Долгота в градусах
            latitude (Optional[float]): Широта в градусах
            baro_altitude (Optional[float]): Барометрическая высота в метрах
            velocity (Optional[float]): Горизонтальная скорость в м/с
            true_track (Optional[float]): Курс в градусах
            vertical_rate (Optional[float]): Вертикальная скорость в м/с
            geo_altitude (Optional[float]): Геометрическая высота в метрах
            on_ground (Optional[bool]): Находится ли самолет на земле
            squawk (Optional[str]): Код ответчика транспондера
            spi (Optional[bool]): Специальный сигнал (emergency/priority)

        Raises:
            ValueError: При невалидных данных
        """
        # Валидация и установка атрибутов через приватные методы
        self._validate_and_set_icao24(icao24)
        self._validate_and_set_callsign(callsign)
        self._validate_and_set_origin_country(origin_country)
        self._validate_and_set_coordinates(longitude, latitude)
        self._validate_and_set_altitude(baro_altitude, geo_altitude)
        self._validate_and_set_velocity(velocity)
        self._validate_and_set_track(true_track)
        self._validate_and_set_vertical_rate(vertical_rate)
        self._validate_and_set_on_ground(on_ground)
        self._validate_and_set_squawk(squawk)
        self._validate_and_set_spi(spi)

    # ========== ПРИВАТНЫЕ МЕТОДЫ ВАЛИДАЦИИ ==========

    def _validate_and_set_icao24(self, icao24: str) -> None:
        """Валидация и установка ICAO24 идентификатора."""
        if not isinstance(icao24, str):
            raise ValueError(f"ICAO24 должен быть строкой, получен {type(icao24)}")

        icao24_cleaned = icao24.strip()

        if not icao24_cleaned:
            raise ValueError("ICAO24 не может быть пустой строкой")

        if len(icao24_cleaned) != 6 and icao24_cleaned != "UNKNOWN":
            raise ValueError(
                f"ICAO24 должен быть 6 символов, получено {len(icao24_cleaned)}"
            )

        self._icao24 = icao24_cleaned

    def _validate_and_set_callsign(self, callsign: Optional[str]) -> None:
        """Валидация и установка позывного."""
        if callsign is None:
            self._callsign = "UNKNOWN"
        elif not isinstance(callsign, str):
            raise ValueError(f"Позывной должен быть строкой, получен {type(callsign)}")
        else:
            self._callsign = callsign.strip() if callsign.strip() else "UNKNOWN"

    def _validate_and_set_origin_country(self, country: Optional[str]) -> None:
        """Валидация и установка страны регистрации."""
        if country is None:
            self._origin_country = "UNKNOWN"
        elif not isinstance(country, str):
            raise ValueError(f"Страна должна быть строкой, получен {type(country)}")
        else:
            country_cleaned = country.strip()
            if not country_cleaned:
                raise ValueError("Страна не может быть пустой строкой")
            self._origin_country = country_cleaned

    def _validate_and_set_coordinates(
        self, longitude: Optional[float], latitude: Optional[float]
    ) -> None:
        """Валидация и установка координат."""
        # Обработка longitude
        if longitude is None:
            self._longitude = 0.0
        elif not isinstance(longitude, (int, float)):
            raise ValueError(f"Долгота должна быть числом, получен {type(longitude)}")
        elif not (-180 <= float(longitude) <= 180):
            raise ValueError(
                f"Долгота должна быть от -180 до 180, получено {longitude}"
            )
        else:
            self._longitude = float(longitude)

        # Обработка latitude
        if latitude is None:
            self._latitude = 0.0
        elif not isinstance(latitude, (int, float)):
            raise ValueError(f"Широта должна быть числом, получен {type(latitude)}")
        elif not (-90 <= float(latitude) <= 90):
            raise ValueError(f"Широта должна быть от -90 до 90, получено {latitude}")
        else:
            self._latitude = float(latitude)

    def _validate_and_set_altitude(
        self, baro_alt: Optional[float], geo_alt: Optional[float]
    ) -> None:
        """Валидация и установка высот."""
        # Обработка baro_altitude
        if baro_alt is None:
            self._baro_altitude = 0.0
        elif not isinstance(baro_alt, (int, float)):
            raise ValueError(
                f"Барометрическая высота должна быть числом, получен {type(baro_alt)}"
            )
        else:
            baro_alt_float = float(baro_alt)
            if baro_alt_float < 0 or baro_alt_float > 20000:
                raise ValueError(
                    f"Нереалистичная барометрическая высота: {baro_alt_float}м"
                )
            self._baro_altitude = baro_alt_float

        # Обработка geo_altitude
        if geo_alt is None:
            self._geo_altitude = 0.0
        elif not isinstance(geo_alt, (int, float)):
            raise ValueError(
                f"Геометрическая высота должна быть числом, получен {type(geo_alt)}"
            )
        else:
            geo_alt_float = float(geo_alt)
            if geo_alt_float < 0 or geo_alt_float > 20000:
                raise ValueError(
                    f"Нереалистичная геометрическая высота: {geo_alt_float}м"
                )
            self._geo_altitude = geo_alt_float

    def _validate_and_set_velocity(self, velocity: Optional[float]) -> None:
        """Валидация и установка скорости."""
        if velocity is None:
            self._velocity = 0.0
        elif not isinstance(velocity, (int, float)):
            raise ValueError(f"Скорость должна быть числом, получен {type(velocity)}")
        else:
            velocity_float = float(velocity)
            if (
                velocity_float < 0 or velocity_float > 1000
            ):  # Максимальная скорость ~3600 км/ч
                raise ValueError(f"Нереалистичная скорость: {velocity_float} м/с")
            self._velocity = velocity_float

    def _validate_and_set_track(self, track: Optional[float]) -> None:
        """Валидация и установка курса."""
        if track is None:
            self._true_track = 0.0
        elif not isinstance(track, (int, float)):
            raise ValueError(f"Курс должен быть числом, получен {type(track)}")
        else:
            self._true_track = float(track) % 360  # Нормализация к 0-360 градусам

    def _validate_and_set_vertical_rate(self, rate: Optional[float]) -> None:
        """Валидация и установка вертикальной скорости."""
        if rate is None:
            self._vertical_rate = 0.0
        elif not isinstance(rate, (int, float)):
            raise ValueError(
                f"Вертикальная скорость должна быть числом, получен {type(rate)}"
            )
        else:
            rate_float = float(rate)
            if abs(rate_float) > 100:  # Максимальная вертикальная скорость ~6000 м/мин
                raise ValueError(
                    f"Нереалистичная вертикальная скорость: {rate_float} м/с"
                )
            self._vertical_rate = rate_float

    def _validate_and_set_on_ground(self, on_ground: Optional[bool]) -> None:
        """Валидация и установка флага 'на земле'."""
        if on_ground is None:
            self._on_ground = False
        elif not isinstance(on_ground, bool):
            raise ValueError(
                f"on_ground должен быть boolean, получен {type(on_ground)}"
            )
        else:
            self._on_ground = on_ground

    def _validate_and_set_squawk(self, squawk: Optional[str]) -> None:
        """Валидация и установка кода ответчика."""
        if squawk is None:
            self._squawk = None
        elif not isinstance(squawk, str):
            raise ValueError(f"Squawk должен быть строкой, получен {type(squawk)}")
        else:
            squawk_cleaned = squawk.strip()
            if not squawk_cleaned.isdigit() or len(squawk_cleaned) != 4:
                raise ValueError(
                    f"Squawk должен быть 4 цифрами, получено '{squawk_cleaned}'"
                )
            self._squawk = squawk_cleaned

    def _validate_and_set_spi(self, spi: Optional[bool]) -> None:
        """Валидация и установка флага специального сигнала."""
        if spi is None:
            self._spi = False
        elif not isinstance(spi, bool):
            raise ValueError(f"SPI должен быть boolean, получен {type(spi)}")
        else:
            self._spi = spi

    # ========== СВОЙСТВА (PROPERTIES) ==========

    @property
    def icao24(self) -> str:
        """Уникальный идентификатор борта (ICAO24)."""
        return self._icao24

    @property
    def callsign(self) -> str:
        """Позывной рейса."""
        return self._callsign

    @property
    def origin_country(self) -> str:
        """Страна регистрации ВС."""
        return self._origin_country

    @property
    def longitude(self) -> float:
        """Долгота в градусах."""
        return self._longitude

    @property
    def latitude(self) -> float:
        """Широта в градусах."""
        return self._latitude

    @property
    def baro_altitude(self) -> float:
        """Барометрическая высота в метрах."""
        return self._baro_altitude

    @property
    def velocity(self) -> float:
        """Горизонтальная скорость в м/с."""
        return self._velocity

    @property
    def velocity_kmh(self) -> float:
        """Скорость в км/ч."""
        return self._velocity * 3.6

    @property
    def true_track(self) -> float:
        """Курс в градусах."""
        return self._true_track

    @property
    def vertical_rate(self) -> float:
        """Вертикальная скорость в м/с."""
        return self._vertical_rate

    @property
    def geo_altitude(self) -> float:
        """Геометрическая высота в метрах."""
        return self._geo_altitude

    @property
    def on_ground(self) -> bool:
        """Находится ли самолет на земле."""
        return self._on_ground

    @property
    def squawk(self) -> Optional[str]:
        """Код ответчика транспондера."""
        return self._squawk

    @property
    def spi(self) -> bool:
        """Специальный сигнал (emergency/priority)."""
        return self._spi

    @property
    def altitude_feet(self) -> float:
        """Высота в футах."""
        return self._baro_altitude * 3.28084

    # ========== МЕТОДЫ СРАВНЕНИЯ ПО ВЫСОТЕ ==========

    def __eq__(self, other: Any) -> bool:
        """Проверка равенства по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return abs(self._baro_altitude - other._baro_altitude) < 0.1

    def __lt__(self, other: Any) -> bool:
        """Сравнение: меньше по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self._baro_altitude < other._baro_altitude

    def __le__(self, other: Any) -> bool:
        """Сравнение: меньше или равно по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self._baro_altitude <= other._baro_altitude

    def __gt__(self, other: Any) -> bool:
        """Сравнение: больше по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self._baro_altitude > other._baro_altitude

    def __ge__(self, other: Any) -> bool:
        """Сравнение: больше или равно по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self._baro_altitude >= other._baro_altitude

    def __ne__(self, other: Any) -> bool:
        """Проверка неравенства по высоте."""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return not self.__eq__(other)

    # ========== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ==========

    def is_climbing(self) -> bool:
        """Проверяет, набирает ли самолет высоту."""
        return self._vertical_rate > 1.0

    def is_descending(self) -> bool:
        """Проверяет, снижается ли самолет."""
        return self._vertical_rate < -1.0

    def is_level(self) -> bool:
        """Проверяет, летит ли самолет горизонтально."""
        return abs(self._vertical_rate) <= 1.0

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
            "icao24": self._icao24,
            "callsign": self._callsign,
            "origin_country": self._origin_country,
            "longitude": self._longitude,
            "latitude": self._latitude,
            "baro_altitude": self._baro_altitude,
            "velocity": self._velocity,
            "true_track": self._true_track,
            "vertical_rate": self._vertical_rate,
            "geo_altitude": self._geo_altitude,
            "on_ground": self._on_ground,
            "squawk": self._squawk,
            "spi": self._spi,
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
        if self._on_ground:
            status = "НА ЗЕМЛЕ"
        else:
            status = f"В ВОЗДУХЕ ({self.altitude_feet:.0f} футов)"

        return (
            f"Рейс {self._callsign} ({self._icao24}) - {self._origin_country}\n"
            f"Положение: {self._latitude:.4f}°N, {self._longitude:.4f}°E\n"
            f"Статус: {status}, Скорость: {self.velocity_kmh:.0f} км/ч\n"
            f"Курс: {self._true_track:.0f}°, "
            f"Верт. скорость: {self._vertical_rate:.1f} м/с"
        )

    def __repr__(self) -> str:
        """Техническое строковое представление."""
        return (
            f"Aircraft(icao24={self._icao24!r}, callsign={self._callsign!r}, "
            f"origin_country={self._origin_country!r}, altitude={self._baro_altitude}m)"
        )
