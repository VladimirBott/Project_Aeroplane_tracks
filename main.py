"""
Основной модуль приложения Aviation Tracker.
Точка входа в программу.
"""

import sys

from src.interface import UserInterface


def main() -> None:
    """
    Основная функция - точка входа в программу.
    """
    try:
        # Создаем и запускаем пользовательский интерфейс
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
