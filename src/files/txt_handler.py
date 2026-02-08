"""
Класс для работы с TXT файлами.
"""

import os
from datetime import datetime
from typing import Any, Dict, List

from src.models.aeroplanes import Aircraft

from .base import BaseFileHandler


class TXTFileHandler(BaseFileHandler):
    """
    Класс для работы с данными о самолетах в формате TXT.

    Сохраняет данные в человекочитаемом текстовом формате.
    """

    def __init__(self, filename: str = "aircraft_data") -> None:
        """
        Инициализация TXT обработчика.

        Args:
            filename (str): Имя файла (без расширения .txt)
        """
        super().__init__(filename)
        self._full_filename = f"{self._filename}.txt"
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создать файл если он не существует."""
        if not os.path.exists(self._full_filename):
            with open(self._full_filename, "w", encoding="utf-8") as f:
                f.write("=== Aviation Tracker Data ===\n\n")

    def _read_data(self) -> List[str]:
        """Прочитать все строки из файла."""
        try:
            with open(self._full_filename, "r", encoding="utf-8") as f:
                return f.readlines()
        except FileNotFoundError:
            return []

    def _write_data(self, lines: List[str]) -> bool:
        """Записать строки в файл."""
        try:
            with open(self._full_filename, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        except Exception:
            return False

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """Добавить самолет в TXT файл."""
        try:
            with open(self._full_filename, "a", encoding="utf-8") as f:
                f.write(f"\n{'=' * 50}\n")
                f.write(f"Самолет: {aircraft.callsign} ({aircraft.icao24})\n")
                f.write(f"Страна: {aircraft.origin_country}\n")
                f.write(
                    f"Координаты: {aircraft.latitude:.4f}°N, {aircraft.longitude:.4f}°E\n"
                )
                f.write(
                    f"Высота: {aircraft.baro_altitude:.0f} м ({aircraft.altitude_feet:.0f} футов)\n"
                )
                f.write(
                    f"Скорость: {aircraft.velocity:.0f} м/с ({aircraft.velocity_kmh:.0f} км/ч)\n"
                )
                f.write(f"Курс: {aircraft.true_track:.0f}°\n")
                f.write(f"Вертикальная скорость: {aircraft.vertical_rate:.1f} м/с\n")
                f.write(f"На земле: {'Да' if aircraft.on_ground else 'Нет'}\n")
                if aircraft.squawk:
                    f.write(f"Squawk: {aircraft.squawk}\n")
                f.write(f"Добавлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'=' * 50}\n")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении в TXT: {e}")
            return False

    def add_aircrafts(self, aircrafts: List[Aircraft]) -> bool:
        """Добавить список самолетов в TXT файл."""
        success = True
        for aircraft in aircrafts:
            if not self.add_aircraft(aircraft):
                success = False
        return success

    def get_all_aircrafts(self) -> List[Dict[str, Any]]:
        """Получить все самолеты из TXT файла (ограниченная функциональность)."""
        # TXT формат сложно парсить обратно в структурированные данные
        print(
            "Внимание: TXT формат не поддерживает полноценное чтение структурированных данных"
        )
        return []

    def get_aircrafts_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Заглушка для TXT формата."""
        print("Функция не поддерживается для TXT формата")
        return []

    def get_top_aircrafts_by_altitude(self, n: int) -> List[Dict[str, Any]]:
        """Заглушка для TXT формата."""
        print("Функция не поддерживается для TXT формата")
        return []

    def delete_aircraft(self, icao24: str) -> bool:
        """Заглушка для TXT формата."""
        print("Функция не поддерживается для TXT формата")
        return False

    def clear_all_data(self) -> bool:
        """Очистить TXT файл."""
        try:
            with open(self._full_filename, "w", encoding="utf-8") as f:
                f.write("=== Aviation Tracker Data ===\n\n")
            return True
        except Exception as e:
            print(f"Ошибка при очистке TXT: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Заглушка для TXT формата."""
        print("Функция не поддерживается для TXT формата")
        return {}
