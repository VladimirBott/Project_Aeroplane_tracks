"""
Тесты для пользовательского интерфейса.
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys

from src.interface.user_interface import UserInterface


class MockAircraft:
    """Мок-объект для самолета."""

    def __init__(self, **kwargs):
        self.icao24 = kwargs.get('icao24', 'test123')
        self.callsign = kwargs.get('callsign', 'TEST01')
        self.origin_country = kwargs.get('origin_country', 'Testland')
        self.latitude = kwargs.get('latitude', 50.0)
        self.longitude = kwargs.get('longitude', 30.0)
        self.baro_altitude = kwargs.get('baro_altitude', 10000.0)
        self.velocity = kwargs.get('velocity', 250.0)
        self.true_track = kwargs.get('true_track', 180.0)
        self.vertical_rate = kwargs.get('vertical_rate', 5.0)
        self.geo_altitude = kwargs.get('geo_altitude', 10000.0)
        self.on_ground = kwargs.get('on_ground', False)
        self.squawk = kwargs.get('squawk', '1234')

        # Вычисляемые свойства
        self.altitude_feet = self.baro_altitude * 3.28084
        self.velocity_kmh = self.velocity * 3.6

    @staticmethod
    def from_opensky_data(data):
        """Статический метод для создания из данных OpenSky."""
        return MockAircraft(
            icao24=data.get(0, 'test123'),
            callsign=data.get(1, 'TEST01'),
            origin_country=data.get(2, 'Testland'),
            longitude=data.get(5, 30.0),
            latitude=data.get(6, 50.0),
            baro_altitude=data.get(7, 10000.0),
            velocity=data.get(9, 250.0),
            true_track=data.get(10, 180.0),
            vertical_rate=data.get(11, 5.0),
            geo_altitude=data.get(13, 10000.0),
            squawk=data.get(14, '1234'),
            on_ground=data.get(8, False)
        )


class TestUserInterface(unittest.TestCase):
    """Тесты для UserInterface."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        # Патчим зависимости с правильными путями
        self.fetcher_patcher = patch('src.interface.user_interface.AircraftDataFetcher')
        self.file_handler_patcher = patch('src.interface.user_interface.JSONFileHandler')

        self.mock_fetcher = self.fetcher_patcher.start()
        self.mock_file_handler = self.file_handler_patcher.start()

        # Создаем UI с моками
        self.ui = UserInterface()
        self.ui.fetcher = self.mock_fetcher.return_value
        self.ui.file_handler = self.mock_file_handler.return_value

    def tearDown(self):
        """Очистка после каждого теста."""
        self.fetcher_patcher.stop()
        self.file_handler_patcher.stop()

    def test_init(self):
        """Тест инициализации интерфейса."""
        ui = UserInterface()
        self.assertIsNotNone(ui.fetcher)
        self.assertIsNotNone(ui.file_handler)
        self.assertIsNone(ui.current_data)

    @patch('builtins.input', return_value='Germany')
    def test_get_country_from_user_valid(self, mock_input):
        """Тест получения страны от пользователя (валидный ввод)."""
        country = self.ui.get_country_from_user()
        self.assertEqual(country, 'Germany')
        mock_input.assert_called_once_with("Страна: ")

    @patch('builtins.input', return_value='')
    def test_get_country_from_user_empty(self, mock_input):
        """Тест получения страны от пользователя (пустой ввод)."""
        country = self.ui.get_country_from_user()
        self.assertIsNone(country)

    @patch('builtins.input', return_value='5')
    def test_get_number_from_user_valid(self, mock_input):
        """Тест получения числа от пользователя (валидный ввод)."""
        with patch('builtins.print') as mock_print:
            n = self.ui.get_number_from_user("Введите число: ")
            self.assertEqual(n, 5)
            mock_print.assert_not_called()  # Не должно быть ошибок

    @patch('builtins.input', return_value='0')
    def test_get_number_from_user_too_small(self, mock_input):
        """Тест получения числа от пользователя (слишком маленькое)."""
        with patch('builtins.print') as mock_print:
            n = self.ui.get_number_from_user("Введите число: ", min_val=1, max_val=10)
            self.assertIsNone(n)
            mock_print.assert_called_once()

    @patch('builtins.input', return_value='abc')
    def test_get_number_from_user_invalid(self, mock_input):
        """Тест получения числа от пользователя (не число)."""
        with patch('builtins.print') as mock_print:
            n = self.ui.get_number_from_user("Введите число: ")
            self.assertIsNone(n)
            mock_print.assert_called_once()

    @patch('builtins.input', return_value='Germany')
    @patch('builtins.print')
    def test_handle_get_aircrafts_by_country_no_data(self, mock_print, mock_input):
        """Тест получения самолетов по стране (нет данных)."""
        # Настраиваем мок fetcher
        mock_result = {
            'aircraft_data': {
                'states': []
            }
        }
        self.ui.fetcher.get_aircraft_data.return_value = mock_result

        # Запускаем тестируемый метод
        self.ui.handle_get_aircrafts_by_country()

        # Проверяем что current_data не установлен
        self.assertIsNone(self.ui.current_data)

        # Проверяем вывод сообщения
        mock_print.assert_any_call("ℹ️  В воздушном пространстве Germany нет самолетов")


    @patch('builtins.input', side_effect=['yes'])
    @patch('builtins.print')
    def test_handle_save_current_data_success(self, mock_print, mock_input):
        """Тест сохранения текущих данных (успех)."""
        # Устанавливаем текущие данные
        self.ui.current_data = [
            MockAircraft(icao24='001', callsign='TEST1'),
            MockAircraft(icao24='002', callsign='TEST2'),
        ]

        # Настраиваем мок file_handler
        self.ui.file_handler.add_aircrafts.return_value = True

        # Запускаем тестируемый метод
        self.ui.handle_save_current_data()

        # Проверяем что данные сохранены
        self.ui.file_handler.add_aircrafts.assert_called_once_with(self.ui.current_data)
        mock_print.assert_any_call("✅ Данные успешно сохранены!")

    def test_handle_save_current_data_no_data(self):
        """Тест сохранения текущих данных (нет данных)."""
        # Убеждаемся что current_data пуст
        self.ui.current_data = None

        with patch('builtins.print') as mock_print:
            # Запускаем тестируемый метод
            self.ui.handle_save_current_data()

            # Проверяем вывод сообщения об ошибке
            mock_print.assert_any_call("❌ Нет текущих данных для сохранения")



    @patch('builtins.input', side_effect=['yes'])
    @patch('builtins.print')
    def test_handle_clear_all_data_success(self, mock_print, mock_input):
        """Тест очистки всех данных (успех)."""
        # Настраиваем мок file_handler
        self.ui.file_handler.clear_all_data.return_value = True

        # Запускаем тестируемый метод
        self.ui.handle_clear_all_data()

        # Проверяем что данные очищены
        self.ui.file_handler.clear_all_data.assert_called_once()
        mock_print.assert_any_call("✅ Все данные успешно удалены!")

    @patch('builtins.print')
    def test_handle_show_all_aircrafts_success(self, mock_print):
        """Тест показа всех самолетов (успех)."""
        # Настраиваем мок file_handler
        mock_aircrafts = [
            {'icao24': '001', 'callsign': 'TEST1', 'origin_country': 'USA', 'baro_altitude': 10000, 'velocity': 250},
            {'icao24': '002', 'callsign': 'TEST2', 'origin_country': 'Russia', 'baro_altitude': 9000, 'velocity': 230},
        ]
        self.ui.file_handler.get_all_aircrafts.return_value = mock_aircrafts

        # Запускаем тестируемый метод
        self.ui.handle_show_all_aircrafts()

        # Проверяем вывод
        mock_print.assert_any_call("📊 Всего сохранено 2 самолетов")

    @patch('builtins.input', side_effect=['abc123', 'yes'])
    @patch('builtins.print')
    def test_handle_delete_aircraft_success(self, mock_print, mock_input):
        """Тест удаления самолета (успех)."""
        # Настраиваем мок file_handler
        self.ui.file_handler.delete_aircraft.return_value = True

        # Запускаем тестируемый метод
        self.ui.handle_delete_aircraft()

        # Проверяем что самолет удален
        self.ui.file_handler.delete_aircraft.assert_called_once_with('abc123')
        mock_print.assert_any_call("✅ Самолет успешно удален!")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_header(self, mock_stdout):
        """Тест вывода заголовка."""
        self.ui.print_header("ТЕСТОВЫЙ ЗАГОЛОВОК")

        output = mock_stdout.getvalue()
        self.assertIn("=" * 60, output)
        self.assertIn("ТЕСТОВЫЙ ЗАГОЛОВОК", output)

    def test_show_aircraft_info(self):
        """Тест отображения информации о самолете."""
        # Создаем тестовый самолет
        aircraft = MockAircraft(
            icao24='test123',
            callsign='TEST01',
            origin_country='Testland',
            baro_altitude=10000.0,
            velocity=250.0,
            latitude=50.0,
            longitude=30.0,
            on_ground=False,
            squawk='1234'
        )

        # Захватываем вывод
        with patch('builtins.print') as mock_print:
            self.ui.show_aircraft_info(aircraft)

            # Проверяем что информация выведена
            calls = [call[0][0] for call in mock_print.call_args_list]
            output = "\n".join(calls)

            self.assertIn("✈️  Рейс: TEST01 (test123)", output)
            self.assertIn("Страна: Testland", output)
            self.assertIn("Высота: 10000 м", output)
            self.assertIn("Положение: 50.00°N, 30.00°E", output)
            self.assertIn("Статус: В воздухе", output)
            self.assertIn("Squawk: 1234", output)



    @patch('builtins.input', return_value='invalid')
    @patch('builtins.print')
    def test_get_user_choice_invalid(self, mock_print, mock_input):
        """Тест получения неверного выбора пользователя."""
        # Нам нужно протестировать взаимодействие, но не запускать бесконечный цикл
        # Поэтому просто проверим вывод
        self.ui.print_menu()
        choice = self.ui.get_user_choice()

        self.assertEqual(choice, 'invalid')


if __name__ == "__main__":
    unittest.main()