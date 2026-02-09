"""
Модуль для взаимодействия с пользователем через консоль.
"""

import logging
import os
import sys
from typing import List, Optional

from src import loggers
from src.api.aircraft_fetcher import AircraftDataFetcher
from src.files.json_handler import JSONFileHandler
from src.models.aeroplanes import Aircraft


class UserInterface:
    """
    Класс для взаимодействия с пользователем через консоль.
    """

    def __init__(self) -> None:
        """Инициализация пользовательского интерфейса."""
        # Автоматически определяем имя логгера на основе имени файла
        current_file = os.path.basename(__file__)  # 'user_interface.py'
        name = os.path.splitext(current_file)[0]  # 'user_interface'
        file_name = f"{name}.log"  # 'user_interface.log'

        # Создаем логгер для этого класса
        self.logger = loggers.create_logger(
            name_logger=name, name_log_file=file_name, logging_level=logging.DEBUG
        )

        self.logger.info("Инициализация UserInterface")

        self.fetcher = AircraftDataFetcher()
        self.file_handler = JSONFileHandler()
        self.current_data: Optional[List[Aircraft]] = None

        self.logger.debug("Компоненты инициализированы")

    def print_header(self, title: str) -> None:
        """Вывести заголовок."""
        print("\n" + "=" * 60)
        print(f" {title.center(58)} ")
        print("=" * 60)

    def print_menu(self) -> None:
        """Вывести главное меню."""
        self.print_header("AVIATION TRACKER")
        print("1. Получить информацию о самолетах по стране")
        print("2. Показать топ N самолетов по высоте из сохраненных данных")
        print("3. Найти самолеты по стране регистрации в сохраненных данных")
        print("4. Сохранить текущие данные в файл")
        print("5. Показать статистику сохраненных данных")
        print("6. Очистить все сохраненные данные")
        print("7. Показать все сохраненные самолеты")
        print("8. Удалить конкретный самолет из сохраненных данных")
        print("0. Выход")
        print("=" * 60)

    def get_user_choice(self) -> str:
        """Получить выбор пользователя."""
        choice = input("\nВыберите действие (0-8): ").strip()
        self.logger.debug(f"Пользователь выбрал: {choice}")
        return choice

    def get_country_from_user(self) -> Optional[str]:
        """Получить название страны от пользователя."""
        print("\nВведите название страны на английском языке")
        print("Примеры: Germany, France, Italy, Spain, Canada, USA")
        country = input("Страна: ").strip()

        if not country:
            print("❌ Название страны не может быть пустым!")
            self.logger.warning("Пользователь ввел пустое название страны")
            return None

        self.logger.info(f"Пользователь выбрал страну: {country}")
        return country

    def get_number_from_user(
        self, prompt: str, min_val: int = 1, max_val: int = 100
    ) -> Optional[int]:
        """Получить число от пользователя с проверкой."""
        try:
            value = input(prompt).strip()
            if not value:
                self.logger.debug("Пользователь не ввел число")
                return None

            n = int(value)
            if n < min_val or n > max_val:
                print(f"❌ Число должно быть от {min_val} до {max_val}!")
                self.logger.warning(
                    f"Число вне диапазона: {n} (допустимо {min_val}-{max_val})"
                )
                return None

            self.logger.debug(f"Пользователь ввел число: {n}")
            return n
        except ValueError:
            print("❌ Пожалуйста, введите целое число!")
            self.logger.warning("Пользователь ввел нечисловое значение")
            return None

    def show_aircraft_info(self, aircraft: Aircraft) -> None:
        """Показать информацию о самолете."""
        print(f"\n✈️  Рейс: {aircraft.callsign} ({aircraft.icao24})")
        print(f"   Страна: {aircraft.origin_country}")
        print(
            f"   Высота: {aircraft.baro_altitude:.0f} м ({aircraft.altitude_feet:.0f} футов)"
        )
        print(f"   Скорость: {aircraft.velocity_kmh:.0f} км/ч")
        print(f"   Положение: {aircraft.latitude:.2f}°N, {aircraft.longitude:.2f}°E")
        print(f"   Статус: {'На земле' if aircraft.on_ground else 'В воздухе'}")
        if aircraft.squawk:
            print(f"   Squawk: {aircraft.squawk}")

    def handle_get_aircrafts_by_country(self) -> None:
        """Обработать запрос информации о самолетах по стране."""
        self.logger.info("Запуск: Получение данных о самолетах по стране")
        self.print_header("ПОЛУЧЕНИЕ ДАННЫХ О САМОЛЕТАХ")

        country = self.get_country_from_user()
        if not country:
            return

        print(f"\n🔄 Получаем данные для {country}...")
        self.logger.info(f"Запрос данных для страны: {country}")

        try:
            result = self.fetcher.get_aircraft_data(country)

            if not result:
                print(f"❌ Не удалось получить данные для {country}")
                self.logger.error(f"Не удалось получить данные для страны: {country}")
                return

            aircraft_data = result.get("aircraft_data", {}).get("states", [])

            if not aircraft_data:
                print(f"ℹ️  В воздушном пространстве {country} нет самолетов")
                self.logger.info(f"Для страны {country} нет данных о самолетах")
                return

            self.logger.info(f"Получено {len(aircraft_data)} записей о самолетах")

            # Создаем объекты Aircraft
            self.current_data = []
            error_count = 0
            for plane_data in aircraft_data:
                try:
                    aircraft = Aircraft.from_opensky_data(plane_data)
                    self.current_data.append(aircraft)
                except ValueError as e:
                    error_count += 1
                    self.logger.warning(f"Ошибка при создании объекта самолета: {e}")

            if error_count > 0:
                self.logger.warning(
                    f"Не удалось создать {error_count} объектов самолетов"
                )

            if not self.current_data:
                print("❌ Не удалось создать объекты самолетов из полученных данных")
                self.logger.error("Не удалось создать ни одного объекта Aircraft")
                return

            print(f"\n✅ Успешно получено {len(self.current_data)} самолетов")
            self.logger.info(f"Создано {len(self.current_data)} объектов Aircraft")

            # Показываем первые 5 самолетов
            print(f"\n📊 Первые 5 самолетов из {len(self.current_data)}:")
            for i, aircraft in enumerate(self.current_data[:5], 1):
                print(f"\n{i}.", end="")
                self.show_aircraft_info(aircraft)

            if len(self.current_data) > 5:
                print(f"\n... и еще {len(self.current_data) - 5} самолетов")

            # Предлагаем сохранить
            print("\n💾 Хотите сохранить эти данные? (да/нет): ", end="")
            save_choice = input().strip().lower()
            self.logger.debug(f"Пользователь выбрал сохранение: {save_choice}")

            if save_choice in ["да", "yes", "y", "д"]:
                success = self.file_handler.add_aircrafts(self.current_data)
                if success:
                    print("✅ Данные успешно сохранены!")
                    self.logger.info(
                        f"Данные успешно сохранены: {len(self.current_data)} самолетов"
                    )
                else:
                    print("❌ Ошибка при сохранении данных")
                    self.logger.error("Ошибка при сохранении данных")
            else:
                self.logger.info("Пользователь отказался от сохранения данных")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.logger.error(
                f"Ошибка при получении данных о самолетах: {e}", exc_info=True
            )

    def handle_show_top_aircrafts(self) -> None:
        """Обработать показ топ N самолетов по высоте."""
        self.logger.info("Запуск: Показ топ самолетов по высоте")
        self.print_header("ТОП САМОЛЕТОВ ПО ВЫСОТЕ")

        n = self.get_number_from_user(
            "Сколько самолетов показать (1-100)? ", min_val=1, max_val=100
        )

        if not n:
            return

        print(f"\n🔄 Получаем топ {n} самолетов по высоте...")
        self.logger.info(f"Запрос топ {n} самолетов по высоте")

        try:
            top_aircrafts = self.file_handler.get_top_aircrafts_by_altitude(n)

            if not top_aircrafts:
                print("ℹ️  В сохраненных данных нет самолетов")
                self.logger.warning("Попытка получить топ самолетов из пустых данных")
                return

            print(f"\n🏆 Топ {n} самолетов по высоте:")
            self.logger.info(f"Получено {len(top_aircrafts)} самолетов в топе")

            for i, aircraft_data in enumerate(top_aircrafts, 1):
                print(f"\n{i}.".ljust(4), end="")
                print(
                    f"Рейс: {aircraft_data.get('callsign', 'N/A')} "
                    f"({aircraft_data.get('icao24', 'N/A')})"
                )
                print("    " + f"Страна: {aircraft_data.get('origin_country', 'N/A')}")
                print("    " + f"Высота: {aircraft_data.get('baro_altitude', 0):.0f} м")
                print(
                    "    "
                    + f"Скорость: {float(aircraft_data.get('velocity', 0)) * 3.6:.0f} км/ч"
                )

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.logger.error(f"Ошибка при получении топ самолетов: {e}", exc_info=True)

    def handle_find_aircrafts_by_country(self) -> None:
        """Обработать поиск самолетов по стране регистрации."""
        self.logger.info("Запуск: Поиск самолетов по стране")
        self.print_header("ПОИСК САМОЛЕТОВ ПО СТРАНЕ")

        country = self.get_country_from_user()
        if not country:
            return

        print(f"\n🔍 Ищем самолеты страны {country}...")
        self.logger.info(f"Поиск самолетов по стране: {country}")

        try:
            aircrafts = self.file_handler.get_aircrafts_by_country(country)

            if not aircrafts:
                print(f"ℹ️  В сохраненных данных нет самолетов из {country}")
                self.logger.info(f"Самолеты страны {country} не найдены")
                return

            print(f"\n✅ Найдено {len(aircrafts)} самолетов из {country}:")
            self.logger.info(f"Найдено {len(aircrafts)} самолетов из {country}")

            for i, aircraft_data in enumerate(aircrafts, 1):
                print(f"\n{i}.".ljust(4), end="")
                print(
                    f"Рейс: {aircraft_data.get('callsign', 'N/A')} "
                    f"({aircraft_data.get('icao24', 'N/A')})"
                )
                print("    " + f"Высота: {aircraft_data.get('baro_altitude', 0):.0f} м")
                print(
                    "    "
                    + f"Скорость: {float(aircraft_data.get('velocity', 0)) * 3.6:.0f} км/ч"
                )

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.logger.error(
                f"Ошибка при поиске самолетов по стране: {e}", exc_info=True
            )

    def handle_save_current_data(self) -> None:
        """Обработать сохранение текущих данных."""
        self.logger.info("Запуск: Сохранение текущих данных")
        self.print_header("СОХРАНЕНИЕ ДАННЫХ")

        if not self.current_data:
            print("❌ Нет текущих данных для сохранения")
            print("Сначала получите данные о самолетах (пункт 1)")
            self.logger.warning("Попытка сохранить отсутствующие данные")
            return

        print(f"📊 Текущие данные содержат {len(self.current_data)} самолетов")
        print("💾 Сохранить? (да/нет): ", end="")

        choice = input().strip().lower()
        self.logger.debug(f"Пользователь выбрал сохранение: {choice}")

        if choice not in ["да", "yes", "y", "д"]:
            print("❌ Сохранение отменено")
            self.logger.info("Пользователь отменил сохранение")
            return

        success = self.file_handler.add_aircrafts(self.current_data)
        if success:
            print("✅ Данные успешно сохранены!")
            self.logger.info(f"Данные сохранены: {len(self.current_data)} самолетов")
        else:
            print("❌ Ошибка при сохранении данных")
            self.logger.error("Ошибка при сохранении данных")

    def handle_show_statistics(self) -> None:
        """Показать статистику сохраненных данных."""
        self.logger.info("Запуск: Показ статистики")
        self.print_header("СТАТИСТИКА СОХРАНЕННЫХ ДАННЫХ")

        try:
            stats = self.file_handler.get_statistics()

            if not stats:
                print("ℹ️  Нет сохраненных данных")
                self.logger.info("Нет данных для статистики")
                return

            print(f"📊 Всего самолетов: {stats.get('total_aircrafts', 0)}")
            self.logger.debug(
                f"Статистика: всего самолетов: {stats.get('total_aircrafts', 0)}"
            )

            # Статистика по странам
            countries = stats.get("countries", {})
            if countries:
                print(f"\n🌍 Самолеты по странам ({len(countries)} стран):")
                self.logger.debug(f"Статистика по {len(countries)} странам")
                for country, count in sorted(
                    countries.items(), key=lambda x: x[1], reverse=True
                )[:10]:
                    print(f"   {country}: {count} самолетов")

                if len(countries) > 10:
                    print(f"   ... и еще {len(countries) - 10} стран")

            # Статистика по высоте
            altitude_stats = stats.get("altitude_stats", {})
            if altitude_stats:
                print("\n📏 Статистика по высоте:")
                print(f"   Минимальная: {altitude_stats.get('min', 0):.0f} м")
                print(f"   Максимальная: {altitude_stats.get('max', 0):.0f} м")
                print(f"   Средняя: {altitude_stats.get('average', 0):.0f} м")

            # Статистика по скорости
            speed_stats = stats.get("speed_stats", {})
            if speed_stats:
                print("\n⚡ Статистика по скорости:")
                print(f"   Минимальная: {speed_stats.get('min', 0) * 3.6:.0f} км/ч")
                print(f"   Максимальная: {speed_stats.get('max', 0) * 3.6:.0f} км/ч")
                print(f"   Средняя: {speed_stats.get('average', 0) * 3.6:.0f} км/ч")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.logger.error(f"Ошибка при получении статистики: {e}", exc_info=True)

    def handle_clear_all_data(self) -> None:
        """Обработать очистку всех данных."""
        self.logger.warning("Запуск: Очистка всех данных")
        self.print_header("ОЧИСТКА ВСЕХ ДАННЫХ")

        print("⚠️  ВНИМАНИЕ: Это действие удалит ВСЕ сохраненные данные!")
        print("Действие необратимо!")
        print("\nВы уверены? (да/нет): ", end="")

        choice = input().strip().lower()
        self.logger.debug(f"Пользователь выбрал очистку: {choice}")

        if choice not in ["да", "yes", "y", "д"]:
            print("❌ Очистка отменена")
            self.logger.info("Пользователь отменил очистку данных")
            return

        success = self.file_handler.clear_all_data()
        if success:
            print("✅ Все данные успешно удалены!")
            self.logger.warning("Все данные успешно удалены")
        else:
            print("❌ Ошибка при удалении данных")
            self.logger.error("Ошибка при удалении всех данных")

    def handle_show_all_aircrafts(self) -> None:
        """Показать все сохраненные самолеты."""
        self.logger.info("Запуск: Показ всех сохраненных самолетов")
        self.print_header("ВСЕ СОХРАНЕННЫЕ САМОЛЕТЫ")

        try:
            aircrafts = self.file_handler.get_all_aircrafts()

            if not aircrafts:
                print("ℹ️  Нет сохраненных данных")
                self.logger.info("Нет сохраненных самолетов")
                return

            print(f"📊 Всего сохранено {len(aircrafts)} самолетов")
            self.logger.debug(f"Получено {len(aircrafts)} самолетов")
            print("\nСписок самолетов:")

            for i, aircraft_data in enumerate(aircrafts, 1):
                print(f"\n{i}.".ljust(4), end="")
                print(
                    f"Рейс: {aircraft_data.get('callsign', 'N/A')} "
                    f"({aircraft_data.get('icao24', 'N/A')})"
                )
                print("    " + f"Страна: {aircraft_data.get('origin_country', 'N/A')}")
                print("    " + f"Высота: {aircraft_data.get('baro_altitude', 0):.0f} м")
                print(
                    "    "
                    + f"Скорость: {float(aircraft_data.get('velocity', 0)) * 3.6:.0f} км/ч"
                )

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.logger.error(
                f"Ошибка при получении всех самолетов: {e}", exc_info=True
            )

    def handle_delete_aircraft(self) -> None:
        """Удалить конкретный самолет."""
        self.logger.info("Запуск: Удаление конкретного самолета")
        self.print_header("УДАЛЕНИЕ САМОЛЕТА")

        icao24 = input("Введите ICAO24 код самолета для удаления: ").strip()

        if not icao24:
            print("❌ Код не может быть пустым!")
            self.logger.warning("Пользователь ввел пустой ICAO24 код")
            return

        print(f"Удалить самолет с кодом {icao24}? (да/нет): ", end="")

        choice = input().strip().lower()
        self.logger.debug(f"Пользователь подтвердил удаление {icao24}: {choice}")

        if choice not in ["да", "yes", "y", "д"]:
            print("❌ Удаление отменено")
            self.logger.info(f"Удаление самолета {icao24} отменено")
            return

        success = self.file_handler.delete_aircraft(icao24)
        if success:
            print("✅ Самолет успешно удален!")
            self.logger.info(f"Самолет {icao24} успешно удален")
        else:
            print("❌ Самолет не найден или ошибка при удалении")
            self.logger.warning(f"Самолет {icao24} не найден при удалении")

    def run(self) -> None:
        """Запустить пользовательский интерфейс."""
        self.logger.info("Запуск Aviation Tracker")
        print("🚀 Запуск Aviation Tracker...")

        while True:
            self.print_menu()
            choice = self.get_user_choice()

            if choice == "0":
                self.logger.info("Пользователь выбрал выход из программы")
                print("\n👋 До свидания!")
                break
            elif choice == "1":
                self.handle_get_aircrafts_by_country()
            elif choice == "2":
                self.handle_show_top_aircrafts()
            elif choice == "3":
                self.handle_find_aircrafts_by_country()
            elif choice == "4":
                self.handle_save_current_data()
            elif choice == "5":
                self.handle_show_statistics()
            elif choice == "6":
                self.handle_clear_all_data()
            elif choice == "7":
                self.handle_show_all_aircrafts()
            elif choice == "8":
                self.handle_delete_aircraft()
            else:
                print("❌ Неверный выбор. Пожалуйста, выберите 0-8")
                self.logger.warning(f"Неверный выбор пользователя: {choice}")

            input("\nНажмите Enter чтобы продолжить...")


def main() -> None:
    """Главная функция для запуска интерфейса."""
    try:
        ui = UserInterface()
        ui.run()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
