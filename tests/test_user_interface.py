"""
Тесты для UserInterface без создания файлов и использования реальных API.
"""

from io import StringIO
from unittest.mock import MagicMock, patch
from src.interface.user_interface import UserInterface
from src.models.aeroplanes import Aircraft


class TestUserInterface:
    """Тесты для UserInterface."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        # Мокаем логгер чтобы не создавать файлы
        with patch("src.interface.user_interface.loggers.create_logger") as mock_logger:
            mock_logger.return_value = MagicMock()

            # Мокаем AircraftDataFetcher
            with patch(
                "src.interface.user_interface.AircraftDataFetcher"
            ) as MockFetcher:
                # Мокаем JSONFileHandler
                with patch(
                    "src.interface.user_interface.JSONFileHandler"
                ) as MockHandler:
                    self.mock_fetcher = MockFetcher.return_value
                    self.mock_handler = MockHandler.return_value

                    # Создаем UI
                    self.ui = UserInterface()

    def test_init(self):
        """Тест инициализации."""
        assert self.ui is not None
        assert hasattr(self.ui, "fetcher")
        assert hasattr(self.ui, "file_handler")
        assert hasattr(self.ui, "current_data")
        assert self.ui.current_data is None

    def test_print_header(self, capsys):
        """Тест вывода заголовка."""
        self.ui.print_header("Тестовый заголовок")
        captured = capsys.readouterr()

        assert "=" * 60 in captured.out
        assert "Тестовый заголовок" in captured.out

    def test_print_menu(self, capsys):
        """Тест вывода меню."""
        self.ui.print_menu()
        captured = capsys.readouterr()

        # Проверяем основные пункты меню
        assert "AVIATION TRACKER" in captured.out
        assert "1. Получить информацию о самолетах по стране" in captured.out
        assert "0. Выход" in captured.out

    @patch("builtins.input", return_value="5")
    def test_get_user_choice(self, mock_input):
        """Тест получения выбора пользователя."""
        choice = self.ui.get_user_choice()
        assert choice == "5"

    @patch("builtins.input")
    def test_get_country_from_user_valid(self, mock_input):
        """Тест получения страны - валидный ввод."""
        mock_input.return_value = "Germany"
        country = self.ui.get_country_from_user()
        assert country == "Germany"

    @patch("builtins.input", return_value="")
    def test_get_country_from_user_empty(self, mock_input, capsys):
        """Тест получения страны - пустой ввод."""
        country = self.ui.get_country_from_user()
        assert country is None

        captured = capsys.readouterr()
        assert "❌ Название страны не может быть пустым!" in captured.out

    @patch("builtins.input", return_value="10")
    def test_get_number_from_user_valid(self, mock_input):
        """Тест получения числа - валидный ввод."""
        number = self.ui.get_number_from_user("Введите число: ", 1, 20)
        assert number == 10

    @patch("builtins.input", return_value="")
    def test_get_number_from_user_empty(self, mock_input):
        """Тест получения числа - пустой ввод."""
        number = self.ui.get_number_from_user("Введите число: ")
        assert number is None

    @patch("builtins.input", return_value="abc")
    def test_get_number_from_user_invalid(self, mock_input, capsys):
        """Тест получения числа - нечисловой ввод."""
        number = self.ui.get_number_from_user("Введите число: ")
        assert number is None

        captured = capsys.readouterr()
        assert "❌ Пожалуйста, введите целое число!" in captured.out

    @patch("builtins.input", return_value="200")
    def test_get_number_from_user_out_of_range(self, mock_input, capsys):
        """Тест получения числа - вне диапазона."""
        number = self.ui.get_number_from_user("Введите число: ", 1, 100)
        assert number is None

        captured = capsys.readouterr()
        assert "❌ Число должно быть от 1 до 100!" in captured.out

    def test_show_aircraft_info(self, capsys):
        """Тест вывода информации о самолете."""
        plane = Aircraft(
            icao24="A0B1C2",
            callsign="SU123",
            origin_country="Russia",
            baro_altitude=10000.0,
            velocity=250.0,
            latitude=55.7558,
            longitude=37.6173,
            on_ground=False,
            squawk="7700",
        )

        self.ui.show_aircraft_info(plane)
        captured = capsys.readouterr()

        assert "SU123" in captured.out
        assert "A0B1C2" in captured.out
        assert "Russia" in captured.out
        assert "10000" in captured.out  # высота
        assert "900" in captured.out  # скорость (250 * 3.6 = 900)
        assert "55.76°N" in captured.out
        assert "37.62°E" in captured.out
        assert "В воздухе" in captured.out
        assert "7700" in captured.out

    @patch("builtins.input", return_value="Germany")
    def test_handle_get_aircrafts_by_country_no_data(self, mock_input, capsys):
        """Тест получения самолетов по стране - нет данных."""
        self.mock_fetcher.get_aircraft_data.return_value = None

        self.ui.handle_get_aircrafts_by_country()

        captured = capsys.readouterr()
        assert "Не удалось получить данные" in captured.out

    @patch("builtins.input", return_value="Germany")
    def test_handle_get_aircrafts_by_country_empty_data(self, mock_input, capsys):
        """Тест получения самолетов по стране - пустые данные."""
        self.mock_fetcher.get_aircraft_data.return_value = {
            "aircraft_data": {"states": []}
        }

        self.ui.handle_get_aircrafts_by_country()

        captured = capsys.readouterr()
        assert "нет самолетов" in captured.out

    @patch("builtins.input", side_effect=["5", "нет"])
    def test_handle_show_top_aircrafts_success(self, mock_input, capsys):
        """Тест показа топ самолетов - успех."""
        test_data = [
            {
                "icao24": "A0B1C2",
                "callsign": "SU123",
                "origin_country": "Russia",
                "baro_altitude": 10000.0,
                "velocity": 250.0,
            },
            {
                "icao24": "D3E4F5",
                "callsign": "BA456",
                "origin_country": "UK",
                "baro_altitude": 8000.0,
                "velocity": 200.0,
            },
        ]

        self.mock_handler.get_top_aircrafts_by_altitude.return_value = test_data

        self.ui.handle_show_top_aircrafts()

        captured = capsys.readouterr()
        assert "Топ 5 самолетов по высоте" in captured.out
        assert "SU123" in captured.out
        assert "A0B1C2" in captured.out

        self.mock_handler.get_top_aircrafts_by_altitude.assert_called_once_with(5)

    @patch("builtins.input", return_value="5")
    def test_handle_show_top_aircrafts_no_data(self, mock_input, capsys):
        """Тест показа топ самолетов - нет данных."""
        self.mock_handler.get_top_aircrafts_by_altitude.return_value = []

        self.ui.handle_show_top_aircrafts()

        captured = capsys.readouterr()
        assert "нет самолетов" in captured.out

    @patch("builtins.input", return_value="Russia")
    def test_handle_find_aircrafts_by_country_success(self, mock_input, capsys):
        """Тест поиска самолетов по стране - успех."""
        test_data = [
            {
                "icao24": "A0B1C2",
                "callsign": "SU123",
                "origin_country": "Russia",
                "baro_altitude": 10000.0,
                "velocity": 250.0,
            }
        ]

        self.mock_handler.get_aircrafts_by_country.return_value = test_data

        self.ui.handle_find_aircrafts_by_country()

        captured = capsys.readouterr()
        assert "Найдено 1 самолетов из Russia" in captured.out
        assert "SU123" in captured.out

        self.mock_handler.get_aircrafts_by_country.assert_called_once_with("Russia")

    @patch("builtins.input", return_value="Germany")
    def test_handle_find_aircrafts_by_country_no_data(self, mock_input, capsys):
        """Тест поиска самолетов по стране - нет данных."""
        self.mock_handler.get_aircrafts_by_country.return_value = []

        self.ui.handle_find_aircrafts_by_country()

        captured = capsys.readouterr()
        assert "нет самолетов" in captured.out

    @patch("builtins.input", side_effect=["да"])
    def test_handle_save_current_data_success(self, mock_input, capsys):
        """Тест сохранения текущих данных - успех."""
        # Устанавливаем текущие данные
        plane = Aircraft(icao24="A0B1C2", callsign="SU123", origin_country="Russia")
        self.ui.current_data = [plane]

        self.mock_handler.add_aircrafts.return_value = True

        self.ui.handle_save_current_data()

        captured = capsys.readouterr()
        assert "Данные успешно сохранены" in captured.out

        self.mock_handler.add_aircrafts.assert_called_once_with([plane])

    @patch("builtins.input", side_effect=["нет"])
    def test_handle_save_current_data_cancel(self, mock_input, capsys):
        """Тест сохранения текущих данных - отмена."""
        plane = Aircraft(icao24="A0B1C2", callsign="SU123", origin_country="Russia")
        self.ui.current_data = [plane]

        self.ui.handle_save_current_data()

        captured = capsys.readouterr()
        assert "Сохранение отменено" in captured.out

        self.mock_handler.add_aircrafts.assert_not_called()

    def test_handle_save_current_data_no_data(self, capsys):
        """Тест сохранения текущих данных - нет данных."""
        self.ui.current_data = None

        self.ui.handle_save_current_data()

        captured = capsys.readouterr()
        assert "Нет текущих данных для сохранения" in captured.out

    def test_handle_show_statistics_success(self, capsys):
        """Тест показа статистики - успех."""
        test_stats = {
            "total_aircrafts": 10,
            "countries": {"Russia": 5, "UK": 3, "Germany": 2},
            "altitude_stats": {"min": 1000, "max": 12000, "average": 6000},
            "speed_stats": {"min": 100, "max": 300, "average": 200},
        }

        self.mock_handler.get_statistics.return_value = test_stats

        self.ui.handle_show_statistics()

        captured = capsys.readouterr()
        assert "Всего самолетов: 10" in captured.out
        assert "Russia: 5 самолетов" in captured.out
        assert "Минимальная: 1000 м" in captured.out
        assert "360 км/ч" in captured.out  # 100 * 3.6

    def test_handle_show_statistics_no_data(self, capsys):
        """Тест показа статистики - нет данных."""
        self.mock_handler.get_statistics.return_value = {}

        self.ui.handle_show_statistics()

        captured = capsys.readouterr()
        assert "Нет сохраненных данных" in captured.out

    @patch("builtins.input", side_effect=["да"])
    def test_handle_clear_all_data_confirm(self, mock_input):
        """Тест очистки всех данных - подтверждение."""
        self.mock_handler.clear_all_data.return_value = True

        self.ui.handle_clear_all_data()

        self.mock_handler.clear_all_data.assert_called_once()

    @patch("builtins.input", side_effect=["нет"])
    def test_handle_clear_all_data_cancel(self, mock_input, capsys):
        """Тест очистки всех данных - отмена."""
        self.ui.handle_clear_all_data()

        captured = capsys.readouterr()
        assert "Очистка отменена" in captured.out

        self.mock_handler.clear_all_data.assert_not_called()

    def test_handle_show_all_aircrafts_success(self, capsys):
        """Тест показа всех самолетов - успех."""
        test_data = [
            {
                "icao24": "A0B1C2",
                "callsign": "SU123",
                "origin_country": "Russia",
                "baro_altitude": 10000.0,
                "velocity": 250.0,
            },
            {
                "icao24": "D3E4F5",
                "callsign": "BA456",
                "origin_country": "UK",
                "baro_altitude": 8000.0,
                "velocity": 200.0,
            },
        ]

        self.mock_handler.get_all_aircrafts.return_value = test_data

        self.ui.handle_show_all_aircrafts()

        captured = capsys.readouterr()
        assert "Всего сохранено 2 самолетов" in captured.out
        assert "SU123" in captured.out
        assert "BA456" in captured.out

    def test_handle_show_all_aircrafts_no_data(self, capsys):
        """Тест показа всех самолетов - нет данных."""
        self.mock_handler.get_all_aircrafts.return_value = []

        self.ui.handle_show_all_aircrafts()

        captured = capsys.readouterr()
        assert "Нет сохраненных данных" in captured.out

    @patch("builtins.input", side_effect=["A0B1C2", "да"])
    def test_handle_delete_aircraft_success(self, mock_input, capsys):
        """Тест удаления самолета - успех."""
        self.mock_handler.delete_aircraft.return_value = True

        self.ui.handle_delete_aircraft()

        captured = capsys.readouterr()
        assert "Самолет успешно удален" in captured.out

        self.mock_handler.delete_aircraft.assert_called_once_with("A0B1C2")

    @patch("builtins.input", side_effect=["A0B1C2", "нет"])
    def test_handle_delete_aircraft_cancel(self, mock_input, capsys):
        """Тест удаления самолета - отмена."""
        self.ui.handle_delete_aircraft()

        captured = capsys.readouterr()
        assert "Удаление отменено" in captured.out

        self.mock_handler.delete_aircraft.assert_not_called()

    @patch("builtins.input", side_effect=["A0B1C2", "да"])
    def test_handle_delete_aircraft_not_found(self, mock_input, capsys):
        """Тест удаления самолета - не найден."""
        self.mock_handler.delete_aircraft.return_value = False

        self.ui.handle_delete_aircraft()

        captured = capsys.readouterr()
        assert "Самолет не найден" in captured.out


class TestUserInterfaceIntegration:
    """Интеграционные тесты UserInterface."""

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_full_run_exit(self, mock_stdout, mock_input):
        """Тест полного запуска с выходом."""
        mock_input.side_effect = ["0"]  # Выход сразу

        # Мокаем все зависимости
        with patch("src.interface.user_interface.loggers.create_logger"):
            with patch("src.interface.user_interface.AircraftDataFetcher"):
                with patch("src.interface.user_interface.JSONFileHandler"):
                    ui = UserInterface()
                    ui.run()

        output = mock_stdout.getvalue()
        assert "AVIATION TRACKER" in output
        assert "До свидания" in output


# Тест главной функции
def test_main_success():
    """Тест главной функции - успех."""
    with patch("src.interface.user_interface.UserInterface") as MockUI:
        mock_ui_instance = MockUI.return_value
        mock_ui_instance.run = MagicMock()

        # Заменяем sys.exit чтобы не прерывать тест
        with patch("sys.exit"):
            from src.interface.user_interface import main

            main()

            mock_ui_instance.run.assert_called_once()


def test_main_keyboard_interrupt():
    """Тест главной функции - прерывание."""
    with patch("src.interface.user_interface.UserInterface") as MockUI:
        mock_ui_instance = MockUI.return_value
        mock_ui_instance.run.side_effect = KeyboardInterrupt

        with patch("sys.exit") as mock_exit:
            from src.interface.user_interface import main

            main()

            mock_exit.assert_called_once_with(0)


def test_main_exception():
    """Тест главной функции - исключение."""
    with patch("src.interface.user_interface.UserInterface") as MockUI:
        mock_ui_instance = MockUI.return_value
        mock_ui_instance.run.side_effect = Exception("Test error")

        with patch("sys.exit") as mock_exit:
            from src.interface.user_interface import main

            main()

            mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    # Простой запуск тестов
    import unittest

    print("🧪 Запуск тестов UserInterface...")

    # Создаем тестовый набор
    loader = unittest.TestLoader()

    # Находим все тестовые классы
    test_classes = [TestUserInterface, TestUserInterfaceIntegration]

    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n📋 Тестируем {test_class.__name__}...")

        # Создаем экземпляр тестового класса
        tester = test_class()

        # Находим все методы test_
        test_methods = [
            method
            for method in dir(tester)
            if method.startswith("test_") and callable(getattr(tester, method))
        ]

        for method_name in test_methods:
            method = getattr(tester, method_name)
            try:
                # Вызываем setup_method если есть
                if hasattr(tester, "setup_method"):
                    tester.setup_method()

                method()
                print(f"  ✅ {method_name}")
                passed += 1

            except AssertionError as e:
                print(f"  ❌ {method_name}: {e}")
                failed += 1
            except Exception as e:
                print(f"  💥 {method_name}: {e}")
                failed += 1

    print(f"\n{'='*50}")
    print(f"📊 Итог: {passed} прошло, {failed} упало")

    if failed == 0:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("❌ Есть неудачные тесты")
