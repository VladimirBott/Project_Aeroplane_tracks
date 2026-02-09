"""
Класс для работы с JSON файлами.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src import loggers
from src.models.aeroplanes import Aircraft

from .base import BaseFileHandler


class JSONFileHandler(BaseFileHandler):
    """
    Класс для работы с данными о самолетах в формате JSON.
    """

    def __init__(self, filename: str = "aircraft_data") -> None:
        """
        Инициализация JSON обработчика.

        Args:
            filename (str): Имя файла (без расширения .json)
        """
        super().__init__(filename)

        # Автоматически определяем имя логгера на основе имени файла
        current_file = os.path.basename(__file__)  # 'json_handler.py'
        name = os.path.splitext(current_file)[0]  # 'json_handler'
        file_name = f"{name}.log"  # 'json_handler.log'

        # Создаем логгер для этого класса
        self.logger = loggers.create_logger(
            name_logger=name,  # 'json_handler'
            name_log_file=file_name,  # 'json_handler.log'
            logging_level=logging.DEBUG,
        )

        # Определяем путь к папке data
        current_dir = Path.cwd()
        self.data_dir = current_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        # Формируем полный путь к файлу
        self._full_filename = self.data_dir / f"{self._filename}.json"

        self.logger.info(
            f"Инициализация JSONFileHandler с файлом: {self._full_filename}"
        )
        self.logger.debug(f"Логгер создан: {name}, файл логов: {file_name}")
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создать файл если он не существует."""
        self.logger.debug(f"Проверка существования файла: {self._full_filename}")

        if not self._full_filename.exists():
            self.logger.info("Файл не существует, создаем новый JSON файл")
            try:
                # Создаем директорию если нет
                self.data_dir.mkdir(parents=True, exist_ok=True)

                # Просто и надежно: создаем файл с валидным пустым JSON
                with open(self._full_filename, "w", encoding="utf-8") as f:
                    f.write("[]")

                self.logger.info(f"Файл успешно создан: {self._full_filename}")

            except Exception as e:
                self.logger.error(f"Ошибка при создании файла: {e}", exc_info=True)
        else:
            file_size = self._full_filename.stat().st_size
            self.logger.debug(f"Файл уже существует, размер: {file_size} байт")

            # Быстрая проверка валидности
            try:
                with open(self._full_filename, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content and content != "[]":

                        json.loads(content)  # Проверяем что это валидный JSON
            except json.JSONDecodeError, ValueError, TypeError:
                self.logger.warning(
                    "Файл содержит невалидный JSON, будет перезаписан при необходимости"
                )

    def _read_data(self) -> List[Dict[str, Any]]:
        """Прочитать все данные из файла."""
        try:
            self.logger.debug(f"Чтение данных из файла: {self._full_filename}")

            if not self._full_filename.exists():
                self.logger.warning(f"Файл не существует: {self._full_filename}")
                return []

            # Сначала читаем как текст для диагностики
            with open(self._full_filename, "r", encoding="utf-8") as f:
                raw_content = f.read()

            self.logger.debug(
                f"Сырое содержимое файла (первые 100 символов): {raw_content[:100]}"
            )

            # Проверяем пустой ли файл
            if not raw_content.strip():
                self.logger.warning("Файл пустой, возвращаем пустой список")
                return []

            try:
                # Пробуем декодировать JSON
                data = json.loads(raw_content)
                self.logger.info(f"Прочитано {len(data)} записей из файла")
                return data

            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка декодирования JSON: {e}", exc_info=True)
                self.logger.error(f"Проблемное содержимое: {raw_content[:200]}")

                # Пробуем исправить: удаляем возможные BOM или невидимые символы
                cleaned_content = raw_content.strip()
                if cleaned_content.startswith("\ufeff"):  # UTF-8 BOM
                    cleaned_content = cleaned_content[1:]

                try:
                    data = json.loads(cleaned_content)
                    self.logger.info("JSON исправлен после очистки")
                    return data
                except json.JSONDecodeError:
                    self.logger.warning("Создаем новый файл из-за поврежденного JSON")
                    try:
                        with open(self._full_filename, "w", encoding="utf-8") as f:
                            f.write("[]")
                        return []
                    except Exception as write_error:
                        self.logger.error(
                            f"Ошибка при создании нового файла: {write_error}"
                        )
                        return []

        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при чтении: {e}", exc_info=True)
            return []

    def _write_data(self, data: List[Dict[str, Any]]) -> bool:
        """Записать данные в файл."""

        try:
            self.logger.debug(f"Запись {len(data)} записей в файл")

            # Убедимся, что папка существует
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Проверяем права на запись
            if self._full_filename.exists():
                if not os.access(str(self._full_filename), os.W_OK):
                    self.logger.error(
                        f"Нет прав на запись в файл: {self._full_filename}"
                    )
                    return False

            with open(self._full_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            file_size = self._full_filename.stat().st_size
            self.logger.info(f"Данные успешно записаны, размер файла: {file_size} байт")
            return True

        except PermissionError as e:
            self.logger.error(f"Ошибка прав доступа: {e}", exc_info=True)
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при записи файла: {e}", exc_info=True)
            return False

    def _aircraft_exists(self, icao24: str, data: List[Dict[str, Any]]) -> bool:
        """Проверить существует ли самолет в данных."""
        exists = any(item.get("icao24") == icao24 for item in data)
        if exists:
            self.logger.debug(f"Самолет с ICAO24={icao24} уже существует в данных")
        return exists

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """Добавить информацию о самолете в JSON файл."""
        self.logger.info(
            f"Добавление самолета: {aircraft.icao24} - {aircraft.callsign}"
        )

        try:
            data = self._read_data()

            if self._aircraft_exists(aircraft.icao24, data):
                self.logger.warning(
                    f"Самолет {aircraft.icao24} уже существует, пропускаем"
                )
                return False

            aircraft_dict = aircraft.to_dict()
            aircraft_dict["_added_at"] = datetime.now().isoformat()
            aircraft_dict["_source"] = "opensky_network"
            data.append(aircraft_dict)

            self.logger.debug(f"Самолет добавлен в данные, всего записей: {len(data)}")

            success = self._write_data(data)
            if success:
                self.logger.info(f"Самолет {aircraft.icao24} успешно сохранен")
            else:
                self.logger.error(f"Ошибка при сохранении самолета {aircraft.icao24}")
            return success

        except Exception as e:
            self.logger.error(
                f"Ошибка при добавлении самолета {aircraft.icao24}: {e}", exc_info=True
            )
            return False

    def add_aircrafts(self, aircrafts: List[Aircraft]) -> bool:
        """Добавить список самолетов в JSON файл."""
        self.logger.info(f"Добавление списка из {len(aircrafts)} самолетов")

        try:
            if not aircrafts:
                self.logger.warning("Список самолетов пуст")
                return True

            data = self._read_data()
            existing_icao24 = {item.get("icao24") for item in data}
            self.logger.debug(
                f"Уже существует {len(existing_icao24)} самолетов в файле"
            )

            added_count = 0
            for aircraft in aircrafts:
                if aircraft.icao24 not in existing_icao24:
                    aircraft_dict = aircraft.to_dict()
                    aircraft_dict["_added_at"] = datetime.now().isoformat()
                    aircraft_dict["_source"] = "opensky_network"
                    data.append(aircraft_dict)
                    existing_icao24.add(aircraft.icao24)
                    added_count += 1
                    self.logger.debug(f"Добавлен самолет {aircraft.icao24}")
                else:
                    self.logger.debug(
                        f"Самолет {aircraft.icao24} уже существует, пропускаем"
                    )

            if added_count > 0:
                self.logger.info(f"Всего новых самолетов для сохранения: {added_count}")
                success = self._write_data(data)
                if success:
                    self.logger.info(f"{added_count} самолетов успешно сохранены")
                else:
                    self.logger.error("Ошибка при сохранении самолетов")
                return success
            else:
                self.logger.info("Нет новых самолетов для добавления")
                return True

        except Exception as e:
            self.logger.error(
                f"Ошибка при добавлении списка самолетов: {e}", exc_info=True
            )
            return False

    def get_all_aircrafts(self) -> List[Dict[str, Any]]:
        """Получить все самолеты из JSON файла."""
        try:
            data = self._read_data()
            result = [
                {k: v for k, v in item.items() if not k.startswith("_")}
                for item in data
            ]
            self.logger.debug(f"Получено {len(result)} самолетов")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при чтении данных: {e}", exc_info=True)
            return []

    def get_aircrafts_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Получить самолеты по стране регистрации."""
        try:
            data = self._read_data()
            result = []
            for item in data:
                if item.get("origin_country", "").lower() == country.lower():
                    clean_item = {
                        k: v for k, v in item.items() if not k.startswith("_")
                    }
                    result.append(clean_item)

            self.logger.info(f"Найдено {len(result)} самолетов из страны: {country}")
            return result
        except Exception as e:
            self.logger.error(
                f"Ошибка при поиске по стране {country}: {e}", exc_info=True
            )
            return []

    def get_top_aircrafts_by_altitude(self, n: int) -> List[Dict[str, Any]]:
        """Получить топ N самолетов по высоте полета."""
        try:
            data = self._read_data()
            sorted_data = sorted(
                data, key=lambda x: x.get("baro_altitude", 0), reverse=True
            )
            top_n = sorted_data[:n]
            result = [
                {k: v for k, v in item.items() if not k.startswith("_")}
                for item in top_n
            ]

            self.logger.info(f"Получен топ {len(result)} самолетов по высоте")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при получении топ самолетов: {e}", exc_info=True)
            return []

    def delete_aircraft(self, icao24: str) -> bool:
        """Удалить информацию о самолете по ICAO24."""
        self.logger.info(f"Удаление самолета с ICAO24: {icao24}")
        try:
            data = self._read_data()
            initial_length = len(data)
            new_data = [item for item in data if item.get("icao24") != icao24]

            if len(new_data) == initial_length:
                self.logger.warning(f"Самолет с ICAO24={icao24} не найден")
                return False

            success = self._write_data(new_data)
            if success:
                self.logger.info(f"Самолет {icao24} успешно удален")
            else:
                self.logger.error(f"Ошибка при удалении самолета {icao24}")
            return success
        except Exception as e:
            self.logger.error(
                f"Ошибка при удалении самолета {icao24}: {e}", exc_info=True
            )
            return False

    def clear_all_data(self) -> bool:
        """Удалить все данные из файла."""
        self.logger.warning("Очистка всех данных из файла")
        try:
            success = self._write_data([])
            if success:
                self.logger.info("Все данные успешно очищены")
            else:
                self.logger.error("Ошибка при очистке данных")
            return success
        except Exception as e:
            self.logger.error(f"Ошибка при очистке данных: {e}", exc_info=True)
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику по данным в JSON файле."""
        try:
            data = self._read_data()

            if not data:
                self.logger.info("Файл пуст, возвращаем пустую статистику")
                return {
                    "total_aircrafts": 0,
                    "countries": {},
                    "file_location": str(self._full_filename),
                }

            countries = {}
            altitudes = []
            speeds = []

            for item in data:
                country = item.get("origin_country", "Unknown")
                countries[country] = countries.get(country, 0) + 1

                altitude = item.get("baro_altitude", 0)
                speed = item.get("velocity", 0)

                if altitude > 0:
                    altitudes.append(altitude)
                if speed > 0:
                    speeds.append(speed)

            avg_altitude = sum(altitudes) / len(altitudes) if altitudes else 0
            avg_speed = sum(speeds) / len(speeds) if speeds else 0

            most_common_country = (
                max(countries.items(), key=lambda x: x[1]) if countries else ("None", 0)
            )

            stats = {
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

            self.logger.info(
                f"Статистика собрана: {len(data)} самолетов, {len(countries)} стран"
            )
            return stats

        except Exception as e:
            self.logger.error(f"Ошибка при получении статистики: {e}", exc_info=True)
            return {}

    def get_aircraft_count(self) -> int:
        """Получить количество самолетов в файле."""
        data = self._read_data()
        count = len(data)
        self.logger.debug(f"Количество самолетов в файле: {count}")
        return count

    def get_countries(self) -> List[str]:
        """Получить список всех стран в файле."""
        data = self._read_data()
        countries = set()
        for item in data:
            country = item.get("origin_country")
            if country:
                countries.add(country)

        result = sorted(list(countries))
        self.logger.debug(f"Найдено {len(result)} уникальных стран")
        return result

    def get_file_path(self) -> str:
        """Получить полный путь к файлу данных."""
        return str(self._full_filename)
