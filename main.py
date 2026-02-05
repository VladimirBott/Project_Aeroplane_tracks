from src.api import AircraftDataFetcher

# 1. Инициализация
tracker = AircraftDataFetcher()

# 2. Получение данных для разных стран
countries = ["Germany", "France", "Italy", "Spain"]

for country in countries:
    print(f"\n=== Получаем данные для {country} ===")
    data = tracker.get_aircraft_data(country)

    if data:
        aircraft_count = len(data['aircraft_data']['states'])
        print(f"Страна: {data['country']}")
        print(f"Самолетов в воздухе: {aircraft_count}")

        # Пример конкретного самолета
        if aircraft_count > 0:
            first_plane = data['aircraft_data']['states'][0]
            print(f"Пример: Рейс {first_plane[1].strip()}, "
                  f"Высота: {first_plane[7]}м")