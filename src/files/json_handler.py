"""
Простой класс для работы с JSON файлами.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from src.models.aeroplanes import Aircraft

from .base import BaseFileHandler


class JSONFileHandler(BaseFileHandler):
    """
    Простой класс для работы с данными о самолетах в формате JSON.
    Файл сохраняется в папку data/ в текущей директории.
    """

    def __init__(self, filename: str = "aircraft_data") -> None:
        """
        Инициализация JSON обработчика.

        Args:
            filename (str): Имя файла (без расширения .json)
        """
        super().__init__(filename)
        self._ensure_file_exists()

    @property
    def file_extension(self) -> str:
        """Расширение файла для JSON."""
        return ".json"

    def _ensure_file_exists(self) -> None:
        """Создать файл если он не существует."""
        if not self.full_path.exists():
            with open(self.full_path, "w", encoding="utf-8") as f:
                f.write("[]")

    def _read_data(self) -> List[Dict[str, Any]]:
        """Прочитать все данные из файла."""
        try:
            with open(self.full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except (
            json.JSONDecodeError,
            FileNotFoundError,
        ):  # ИСПРАВЛЕНО: правильный синтаксис
            # Если файл поврежден или не найден, создаем заново
            self._ensure_file_exists()
            return []
        except Exception as e:  # Дополнительно: перехватываем все остальные исключения
            print(f"Ошибка при чтении файла: {e}")
            return []

    def _write_data(self, data: List[Dict[str, Any]]) -> bool:
        """Записать данные в файл."""
        try:
            with open(self.full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except (
            IOError,
            PermissionError,
            OSError,
        ) as e:  # ИСПРАВЛЕНО: конкретные исключения
            print(f"Ошибка записи в файл: {e}")
            return False
        except Exception as e:  # Для всех остальных исключений
            print(f"Неожиданная ошибка: {e}")
            return False

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """Добавить информацию о самолете в JSON файл."""
        data = self._read_data()

        # Проверяем, нет ли уже такого самолета
        if any(item.get("icao24") == aircraft.icao24 for item in data):
            return False

        aircraft_dict = aircraft.to_dict()
        aircraft_dict["_added_at"] = datetime.now().isoformat()
        data.append(aircraft_dict)

        return self._write_data(data)

    def add_aircrafts(self, aircrafts: List[Aircraft]) -> bool:
        """Добавить список самолетов в JSON файл."""
        if not aircrafts:
            return True

        data = self._read_data()
        existing_icao24 = {item.get("icao24") for item in data}

        added = False
        for aircraft in aircrafts:
            if aircraft.icao24 not in existing_icao24:
                aircraft_dict = aircraft.to_dict()
                aircraft_dict["_added_at"] = datetime.now().isoformat()
                data.append(aircraft_dict)
                existing_icao24.add(aircraft.icao24)
                added = True

        if added:
            return self._write_data(data)
        return True

    def get_all_aircrafts(self) -> List[Dict[str, Any]]:
        """Получить все самолеты из JSON файла."""
        data = self._read_data()
        # Убираем служебные поля (начинающиеся с _)
        return [
            {k: v for k, v in item.items() if not k.startswith("_")} for item in data
        ]

    def get_aircrafts_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Получить самолеты по стране регистрации."""
        data = self._read_data()
        result = []
        for item in data:
            if item.get("origin_country", "").lower() == country.lower():
                clean_item = {k: v for k, v in item.items() if not k.startswith("_")}
                result.append(clean_item)
        return result

    def get_top_aircrafts_by_altitude(self, n: int) -> List[Dict[str, Any]]:
        """Получить топ N самолетов по высоте полета."""
        data = self._read_data()
        sorted_data = sorted(
            data, key=lambda x: x.get("baro_altitude", 0), reverse=True
        )
        top_n = sorted_data[:n]
        return [
            {k: v for k, v in item.items() if not k.startswith("_")} for item in top_n
        ]

    def delete_aircraft(self, icao24: str) -> bool:
        """Удалить информацию о самолете по ICAO24."""
        data = self._read_data()
        new_data = [item for item in data if item.get("icao24") != icao24]

        if len(new_data) == len(data):
            return False  # Не нашли для удаления

        return self._write_data(new_data)

    def clear_all_data(self) -> bool:
        """Удалить все данные из файла."""
        return self._write_data([])

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику по данным в JSON файле."""
        data = self._read_data()

        if not data:
            return {"total_aircrafts": 0}

        from collections import Counter

        countries = Counter(item.get("origin_country", "Unknown") for item in data)

        altitudes = [
            item.get("baro_altitude", 0)
            for item in data
            if item.get("baro_altitude", 0) > 0
        ]
        speeds = [
            item.get("velocity", 0) for item in data if item.get("velocity", 0) > 0
        ]

        # ИСПРАВЛЕНО: most_common_country теперь словарь
        most_common_tuple = countries.most_common(1)[0] if countries else ("None", 0)

        return {
            "total_aircrafts": len(data),
            "unique_countries": len(countries),
            "most_common_country": {
                "country": most_common_tuple[0],
                "count": most_common_tuple[1],
            },
            "altitude_stats": {
                "min": min(altitudes) if altitudes else 0,
                "max": max(altitudes) if altitudes else 0,
                "average": sum(altitudes) / len(altitudes) if altitudes else 0,
            },
            "speed_stats": {
                "min": min(speeds) if speeds else 0,
                "max": max(speeds) if speeds else 0,
                "average": sum(speeds) / len(speeds) if speeds else 0,
            },
        }

    def get_file_info(self) -> Dict[str, Any]:
        """Получить информацию о файле."""
        if not self.full_path.exists():
            return {
                "filename": str(self.full_path),
                "exists": False,
                "size_bytes": 0,
            }

        try:
            return {
                "filename": str(self.full_path),
                "exists": True,
                "size_bytes": self.full_path.stat().st_size,
            }
        except OSError as e:
            print(f"Ошибка получения информации о файле: {e}")
            return {
                "filename": str(self.full_path),
                "exists": False,
                "size_bytes": 0,
            }
