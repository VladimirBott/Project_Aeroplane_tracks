"""
Основной модуль приложения.
"""

from src.interface.user_interface import UserInterface


def main():
    """Основная функция приложения."""
    print("✈️  Aeroplane Tracker")
    print("=" * 40)

    try:
        ui = UserInterface()
        ui.run()
    except KeyboardInterrupt:
        print("\n\n👋 Выход из программы")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
