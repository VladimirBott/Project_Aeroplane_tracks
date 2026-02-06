"""
Модуль для взаимодействия с пользователем через консоль.
"""

import sys
from typing import Any, Dict, List, Optional

from src.api.aircraft_fetcher import AircraftDataFetcher
from src.files import JSONFileHandler
from src.models.aeroplanes import Aircraft


class UserInterface:
    """
    Класс для взаимодействия с пользователем через консоль.

    Предоставляет возможности:
    1. Запрос информации о самолетах по стране
    2. Получение топ N самолетов по высоте
    3. Получение самолетов по стране регистрации
    4. Сохранение данных в файл
    5. Просмотр статистики
    """

    def __init__(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.fetcher = AircraftDataFetcher()
        self.file_handler = JSONFileHandler()
        self.current_data: Optional[List[Aircraft]] = None

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
        return input("\nВыберите действие (0-8): ").strip()

    def get_country_from_user(self) -> Optional[str]:
        """Получить название страны от пользователя."""
        print("\nВведите название страны на английском языке")
        print("Примеры: Germany, France, Italy, Spain, Canada, USA")
        country = input("Страна: ").strip()

        if not country:
            print("❌ Название страны не может быть пустым!")
            return None

        return country

    def get_number_from_user(
        self, prompt: str, min_val: int = 1, max_val: int = 100
    ) -> Optional[int]:
        """Получить число от пользователя с проверкой."""
        try:
            value = input(prompt).strip()
            if not value:
                return None

            n = int(value)
            if n < min_val or n > max_val:
                print(f"❌ Число должно быть от {min_val} до {max_val}!")
                return None

            return n
        except ValueError:
            print("❌ Пожалуйста, введите целое число!")
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
        self.print_header("ПОЛУЧЕНИЕ ДАННЫХ О САМОЛЕТАХ")

        country = self.get_country_from_user()
        if not country:
            return

        print(f"\n🔄 Получаем данные для {country}...")

        try:
            result = self.fetcher.get_aircraft_data(country)

            if not result:
                print(f"❌ Не удалось получить данные для {country}")
                return

            aircraft_data = result.get("aircraft_data", {}).get("states", [])

            if not aircraft_data:
                print(f"ℹ️  В воздушном пространстве {country} нет самолетов")
                return

            # Создаем объекты Aircraft
            self.current_data = []
            for plane_data in aircraft_data:
                try:
                    aircraft = Aircraft.from_opensky_data(plane_data)
                    self.current_data.append(aircraft)
                except ValueError as e:
                    print(f"⚠️  Ошибка при создании объекта самолета: {e}")

            if not self.current_data:
                print("❌ Не удалось создать объекты самолетов из полученных данных")
                return

            print(f"\n✅ Успешно получено {len(self.current_data)} самолетов")

            # Показываем первые 5 самолетов
            print(f"\n📊 Первые 5 самолетов из {len(self.current_data)}:")
            for i, aircraft in enumerate(self.current_data[:5], 1):
                print(f"\n{i}.", end="")
                self.show_aircraft_info(aircraft)

            if len(self.current_data) > 5:
                print(f"\n... и еще {len(self.current_data) - 5} самолетов")

            # Предлагаем сохранить
            print(f"\n💾 Хотите сохранить эти данные? (да/нет): ", end="")
            save_choice = input().strip().lower()

            if save_choice in ["да", "yes", "y", "д"]:
                success = self.file_handler.add_aircrafts(self.current_data)
                if success:
                    print("✅ Данные успешно сохранены!")
                else:
                    print("❌ Ошибка при сохранении данных")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def handle_show_top_aircrafts(self) -> None:
        """Обработать показ топ N самолетов по высоте."""
        self.print_header("ТОП САМОЛЕТОВ ПО ВЫСОТЕ")

        n = self.get_number_from_user(
            f"Сколько самолетов показать (1-100)? ", min_val=1, max_val=100
        )

        if not n:
            return

        print(f"\n🔄 Получаем топ {n} самолетов по высоте...")

        try:
            top_aircrafts = self.file_handler.get_top_aircrafts_by_altitude(n)

            if not top_aircrafts:
                print("ℹ️  В сохраненных данных нет самолетов")
                return

            print(f"\n🏆 Топ {n} самолетов по высоте:")

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

    def handle_find_aircrafts_by_country(self) -> None:
        """Обработать поиск самолетов по стране регистрации."""
        self.print_header("ПОИСК САМОЛЕТОВ ПО СТРАНЕ")

        country = self.get_country_from_user()
        if not country:
            return

        print(f"\n🔍 Ищем самолеты страны {country}...")

        try:
            aircrafts = self.file_handler.get_aircrafts_by_country(country)

            if not aircrafts:
                print(f"ℹ️  В сохраненных данных нет самолетов из {country}")
                return

            print(f"\n✅ Найдено {len(aircrafts)} самолетов из {country}:")

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

    def handle_save_current_data(self) -> None:
        """Обработать сохранение текущих данных."""
        self.print_header("СОХРАНЕНИЕ ДАННЫХ")

        if not self.current_data:
            print("❌ Нет текущих данных для сохранения")
            print("Сначала получите данные о самолетах (пункт 1)")
            return

        print(f"📊 Текущие данные содержат {len(self.current_data)} самолетов")
        print("💾 Сохранить? (да/нет): ", end="")

        choice = input().strip().lower()
        if choice not in ["да", "yes", "y", "д"]:
            print("❌ Сохранение отменено")
            return

        success = self.file_handler.add_aircrafts(self.current_data)
        if success:
            print("✅ Данные успешно сохранены!")
        else:
            print("❌ Ошибка при сохранении данных")

    def handle_show_statistics(self) -> None:
        """Показать статистику сохраненных данных."""
        self.print_header("СТАТИСТИКА СОХРАНЕННЫХ ДАННЫХ")

        try:
            stats = self.file_handler.get_statistics()

            if not stats:
                print("ℹ️  Нет сохраненных данных")
                return

            print(f"📊 Всего самолетов: {stats.get('total_aircrafts', 0)}")

            # Статистика по странам
            countries = stats.get("countries", {})
            if countries:
                print(f"\n🌍 Самолеты по странам ({len(countries)} стран):")
                for country, count in sorted(
                    countries.items(), key=lambda x: x[1], reverse=True
                )[:10]:
                    print(f"   {country}: {count} самолетов")

                if len(countries) > 10:
                    print(f"   ... и еще {len(countries) - 10} стран")

            # Статистика по высоте
            altitude_stats = stats.get("altitude_stats", {})
            if altitude_stats:
                print(f"\n📏 Статистика по высоте:")
                print(f"   Минимальная: {altitude_stats.get('min', 0):.0f} м")
                print(f"   Максимальная: {altitude_stats.get('max', 0):.0f} м")
                print(f"   Средняя: {altitude_stats.get('average', 0):.0f} м")

            # Статистика по скорости
            speed_stats = stats.get("speed_stats", {})
            if speed_stats:
                print(f"\n⚡ Статистика по скорости:")
                print(f"   Минимальная: {speed_stats.get('min', 0) * 3.6:.0f} км/ч")
                print(f"   Максимальная: {speed_stats.get('max', 0) * 3.6:.0f} км/ч")
                print(f"   Средняя: {speed_stats.get('average', 0) * 3.6:.0f} км/ч")

            # Самая распространенная страна
            most_common = stats.get("most_common_country", {})
            if most_common:
                print(f"\n🏆 Самая распространенная страна:")
                print(
                    f"   {most_common.get('country', 'N/A')}: "
                    f"{most_common.get('count', 0)} самолетов"
                )

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def handle_clear_all_data(self) -> None:
        """Обработать очистку всех данных."""
        self.print_header("ОЧИСТКА ВСЕХ ДАННЫХ")

        print("⚠️  ВНИМАНИЕ: Это действие удалит ВСЕ сохраненные данные!")
        print("Действие необратимо!")
        print("\nВы уверены? (да/нет): ", end="")

        choice = input().strip().lower()
        if choice not in ["да", "yes", "y", "д"]:
            print("❌ Очистка отменена")
            return

        success = self.file_handler.clear_all_data()
        if success:
            print("✅ Все данные успешно удалены!")
        else:
            print("❌ Ошибка при удалении данных")

    def handle_show_all_aircrafts(self) -> None:
        """Показать все сохраненные самолеты."""
        self.print_header("ВСЕ СОХРАНЕННЫЕ САМОЛЕТЫ")

        try:
            aircrafts = self.file_handler.get_all_aircrafts()

            if not aircrafts:
                print("ℹ️  Нет сохраненных данных")
                return

            print(f"📊 Всего сохранено {len(aircrafts)} самолетов")
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

    def handle_delete_aircraft(self) -> None:
        """Удалить конкретный самолет."""
        self.print_header("УДАЛЕНИЕ САМОЛЕТА")

        icao24 = input("Введите ICAO24 код самолета для удаления: ").strip()

        if not icao24:
            print("❌ Код не может быть пустым!")
            return

        print(f"Удалить самолет с кодом {icao24}? (да/нет): ", end="")

        choice = input().strip().lower()
        if choice not in ["да", "yes", "y", "д"]:
            print("❌ Удаление отменено")
            return

        success = self.file_handler.delete_aircraft(icao24)
        if success:
            print("✅ Самолет успешно удален!")
        else:
            print("❌ Самолет не найден или ошибка при удалении")

    def run(self) -> None:
        """Запустить пользовательский интерфейс."""
        print("🚀 Запуск Aviation Tracker...")

        while True:
            self.print_menu()
            choice = self.get_user_choice()

            if choice == "0":
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
