"""
Класс для работы с JSON файлами.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models.aeroplanes import Aircraft

from .base import BaseFileHandler


class JSONFileHandler(BaseFileHandler):
    """
    Класс для работы с данными о самолетах в формате JSON.

    Сохраняет данные в виде списка словарей, соответствующих атрибутам
    класса Aircraft. Файл не перезаписывается при каждом запуске,
    а добавляет данные без дублирования.
    Файл сохраняется в папку data в корне проекта.
    """

    def __init__(self, filename: str = "aircraft_data") -> None:
        """
        Инициализация JSON обработчика.

        Args:
            filename (str): Имя файла (без расширения .json)
        """
        super().__init__(filename)

        # Определяем путь к папке data
        current_dir = Path.cwd()  # Текущая директория (корень проекта)
        self.data_dir = current_dir / "data"

        # Создаем папку data если она не существует
        self.data_dir.mkdir(exist_ok=True)

        # Формируем полный путь к файлу
        self._full_filename = self.data_dir / f"{self._filename}.json"

        print(f"[DEBUG] Инициализация JSONFileHandler")
        print(f"[DEBUG] Текущая директория: {current_dir}")
        print(f"[DEBUG] Путь к папке data: {self.data_dir}")
        print(f"[DEBUG] Полный путь к файлу: {self._full_filename}")

        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создать файл если он не существует."""
        print(f"[DEBUG] Проверка существования файла: {self._full_filename}")

        if not self._full_filename.exists():
            print(f"[DEBUG] Файл не существует, создаем...")
            try:
                # Убедимся, что папка существует
                self.data_dir.mkdir(parents=True, exist_ok=True)

                with open(self._full_filename, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                print(f"[DEBUG] Файл успешно создан в {self._full_filename}")
            except Exception as e:
                print(f"[DEBUG] Ошибка при создании файла: {e}")
                print(f"[DEBUG] Текущая директория: {Path.cwd()}")
        else:
            file_size = self._full_filename.stat().st_size
            print(f"[DEBUG] Файл уже существует, размер: {file_size} байт")

    def _read_data(self) -> List[Dict[str, Any]]:
        """
        Прочитать все данные из файла.

        Returns:
            List[Dict[str, Any]]: Данные из файла
        """
        try:
            print(f"[DEBUG] Чтение данных из файла: {self._full_filename}")

            # Проверяем существует ли файл
            if not self._full_filename.exists():
                print(f"[DEBUG] Файл не существует, возвращаем пустой список")
                return []

            with open(self._full_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"[DEBUG] Прочитано {len(data)} записей из {self._full_filename}")
                return data
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Ошибка декодирования JSON: {e}")
            # Если файл поврежден, создаем новый
            print(f"[DEBUG] Создаем новый файл...")
            with open(self._full_filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            return []
        except Exception as e:
            print(f"[DEBUG] Неожиданная ошибка при чтении: {e}")
            return []

    def _write_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Записать данные в файл.

        Args:
            data (List[Dict[str, Any]]): Данные для записи

        Returns:
            bool: True если успешно
        """
        try:
            print(f"[DEBUG] Запись {len(data)} записей в файл")
            print(f"[DEBUG] Путь к файлу: {self._full_filename}")

            # Убедимся, что папка существует
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Проверяем права на запись
            if self._full_filename.exists():
                if not os.access(str(self._full_filename), os.W_OK):
                    print(f"[DEBUG] ОШИБКА: Нет прав на запись в файл!")
                    return False

            with open(self._full_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            file_size = self._full_filename.stat().st_size
            print(f"[DEBUG] Данные успешно записаны в {self._full_filename}")
            print(f"[DEBUG] Новый размер файла: {file_size} байт")
            return True
        except PermissionError as e:
            print(f"[DEBUG] ОШИБКА ПРАВ ДОСТУПА: {e}")
            return False
        except Exception as e:
            print(f"[DEBUG] Ошибка при записи файла: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _aircraft_exists(self, icao24: str, data: List[Dict[str, Any]]) -> bool:
        """
        Проверить существует ли самолет в данных.

        Args:
            icao24 (str): Идентификатор самолета
            data (List[Dict[str, Any]]): Данные для проверки

        Returns:
            bool: True если существует
        """
        for item in data:
            if item.get("icao24") == icao24:
                return True
        return False

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """
        Добавить информацию о самолете в JSON файл.

        Args:
            aircraft (Aircraft): Объект самолета

        Returns:
            bool: True если успешно, False если ошибка
        """
        print(f"\n[DEBUG] Добавление самолета: {aircraft.icao24} - {aircraft.callsign}")

        try:
            # Читаем существующие данные
            data = self._read_data()

            # Проверяем нет ли уже такого самолета
            if self._aircraft_exists(aircraft.icao24, data):
                print(f"[DEBUG] Самолет {aircraft.icao24} уже существует, пропускаем")
                return False  # Не добавляем дубликаты

            # Преобразуем самолет в словарь
            aircraft_dict = aircraft.to_dict()

            # Добавляем метаданные
            aircraft_dict["_added_at"] = datetime.now().isoformat()
            aircraft_dict["_source"] = "opensky_network"

            # Добавляем в данные
            data.append(aircraft_dict)
            print(f"[DEBUG] Самолет добавлен в данные, всего записей: {len(data)}")

            # Записываем обратно
            success = self._write_data(data)
            if success:
                print(f"[DEBUG] ✅ Самолет успешно сохранен в {self._full_filename}")
            else:
                print(f"[DEBUG] ❌ Ошибка при сохранении самолета")

            return success

        except Exception as e:
            print(f"[DEBUG] ❌ Ошибка при добавлении самолета: {e}")
            import traceback

            traceback.print_exc()
            return False

    def add_aircrafts(self, aircrafts: List[Aircraft]) -> bool:
        """
        Добавить список самолетов в JSON файл.

        Args:
            aircrafts (List[Aircraft]): Список объектов самолетов

        Returns:
            bool: True если успешно, False если ошибка
        """
        print(f"\n[DEBUG] Добавление списка из {len(aircrafts)} самолетов")
        print(f"[DEBUG] Файл будет сохранен в: {self._full_filename}")

        try:
            if not aircrafts:
                print("[DEBUG] Список самолетов пуст")
                return True

            # Читаем существующие данные
            data = self._read_data()
            existing_icao24 = {item.get("icao24") for item in data}
            print(f"[DEBUG] Уже существует {len(existing_icao24)} самолетов в файле")

            # Добавляем только новые самолеты
            added_count = 0
            for aircraft in aircrafts:
                if aircraft.icao24 not in existing_icao24:
                    aircraft_dict = aircraft.to_dict()
                    aircraft_dict["_added_at"] = datetime.now().isoformat()
                    aircraft_dict["_source"] = "opensky_network"
                    data.append(aircraft_dict)
                    existing_icao24.add(aircraft.icao24)
                    added_count += 1
                    print(f"[DEBUG] Добавлен самолет {aircraft.icao24}")
                else:
                    print(
                        f"[DEBUG] Самолет {aircraft.icao24} уже существует, пропускаем"
                    )

            if added_count > 0:
                print(f"[DEBUG] Всего новых самолетов для сохранения: {added_count}")
                success = self._write_data(data)
                if success:
                    print(
                        f"[DEBUG] ✅ {added_count} самолетов успешно сохранены в {self._full_filename}"
                    )
                else:
                    print(f"[DEBUG] ❌ Ошибка при сохранении самолетов")
                return success
            else:
                print("[DEBUG] Нет новых самолетов для добавления")
                return True

        except Exception as e:
            print(f"[DEBUG] ❌ Ошибка при добавлении списка самолетов: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_all_aircrafts(self) -> List[Dict[str, Any]]:
        """
        Получить все самолеты из JSON файла.

        Returns:
            List[Dict[str, Any]]: Список словарей с данными самолетов
        """
        try:
            data = self._read_data()
            # Убираем служебные поля из вывода
            return [
                {k: v for k, v in item.items() if not k.startswith("_")}
                for item in data
            ]
        except Exception as e:
            print(f"Ошибка при чтении данных: {e}")
            return []

    def get_aircrafts_by_country(self, country: str) -> List[Dict[str, Any]]:
        """
        Получить самолеты по стране регистрации.

        Args:
            country (str): Страна регистрации

        Returns:
            List[Dict[str, Any]]: Список самолетов указанной страны
        """
        try:
            data = self._read_data()
            result = []

            for item in data:
                if item.get("origin_country", "").lower() == country.lower():
                    # Убираем служебные поля
                    clean_item = {
                        k: v for k, v in item.items() if not k.startswith("_")
                    }
                    result.append(clean_item)

            return result
        except Exception as e:
            print(f"Ошибка при поиске по стране: {e}")
            return []

    def get_top_aircrafts_by_altitude(self, n: int) -> List[Dict[str, Any]]:
        """
        Получить топ N самолетов по высоте полета.

        Args:
            n (int): Количество самолетов в топе

        Returns:
            List[Dict[str, Any]]: Топ N самолетов по высоте
        """
        try:
            data = self._read_data()

            # Сортируем по высоте (по убыванию)
            sorted_data = sorted(
                data, key=lambda x: x.get("baro_altitude", 0), reverse=True
            )

            # Берем первые N элементов
            top_n = sorted_data[:n]

            # Убираем служебные поля
            result = [
                {k: v for k, v in item.items() if not k.startswith("_")}
                for item in top_n
            ]

            return result
        except Exception as e:
            print(f"Ошибка при получении топ самолетов: {e}")
            return []

    def delete_aircraft(self, icao24: str) -> bool:
        """
        Удалить информацию о самолете по ICAO24.

        Args:
            icao24 (str): Уникальный идентификатор самолета

        Returns:
            bool: True если успешно удалено, False если не найдено
        """
        try:
            data = self._read_data()
            initial_length = len(data)

            # Фильтруем данные, удаляя самолет с указанным icao24
            new_data = [item for item in data if item.get("icao24") != icao24]

            if len(new_data) == initial_length:
                return False  # Самолет не найден

            return self._write_data(new_data)
        except Exception as e:
            print(f"Ошибка при удалении самолета: {e}")
            return False

    def clear_all_data(self) -> bool:
        """
        Удалить все данные из файла.

        Returns:
            bool: True если успешно
        """
        try:
            return self._write_data([])
        except Exception as e:
            print(f"Ошибка при очистке данных: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по данным в JSON файле.

        Returns:
            Dict[str, Any]: Статистика
        """
        try:
            data = self._read_data()

            if not data:
                return {
                    "total_aircrafts": 0,
                    "countries": {},
                    "altitude_stats": {},
                    "speed_stats": {},
                    "file_location": str(self._full_filename),
                }

            # Собираем статистику
            countries = {}
            altitudes = []
            speeds = []

            for item in data:
                # Статистика по странам
                country = item.get("origin_country", "Unknown")
                countries[country] = countries.get(country, 0) + 1

                # Собираем высоты и скорости
                altitude = item.get("baro_altitude", 0)
                speed = item.get("velocity", 0)

                if altitude > 0:
                    altitudes.append(altitude)
                if speed > 0:
                    speeds.append(speed)

            # Вычисляем средние значения
            avg_altitude = sum(altitudes) / len(altitudes) if altitudes else 0
            avg_speed = sum(speeds) / len(speeds) if speeds else 0

            # Находим самую распространенную страну
            most_common_country = (
                max(countries.items(), key=lambda x: x[1]) if countries else ("None", 0)
            )

            return {
                "total_aircrafts": len(data),
                "countries": countries,
                "altitude_stats": {
                    "min": min(altitudes) if altitudes else 0,
                    "max": max(altitudes) if altitudes else 0,
                    "average": avg_altitude,
                },
                "speed_stats": {
                    "min": min(speeds) if speeds else 0,
                    "max": max(speeds) if speeds else 0,
                    "average": avg_speed,
                },
                "most_common_country": {
                    "country": most_common_country[0],
                    "count": most_common_country[1],
                },
                "file_location": str(self._full_filename),
            }
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return {}

    def get_aircraft_count(self) -> int:
        """
        Получить количество самолетов в файле.

        Returns:
            int: Количество самолетов
        """
        data = self._read_data()
        return len(data)

    def get_countries(self) -> List[str]:
        """
        Получить список всех стран в файле.

        Returns:
            List[str]: Список стран
        """
        data = self._read_data()
        countries = set()

        for item in data:
            country = item.get("origin_country")
            if country:
                countries.add(country)

        return sorted(list(countries))

    def get_file_path(self) -> str:
        """
        Получить полный путь к файлу данных.

        Returns:
            str: Полный путь к файлу
        """
        return str(self._full_filename)
