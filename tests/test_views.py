import json
from unittest.mock import patch, Mock
from src.views import main

def test_main_builds_expected_json_with_all_apis_mocked():
    # --- Подготавливаем фейковые данные ---
    fake_greeting = "Добрый день"
    fake_df = object()  # маркер, возвращаемый read_file

    fake_card_ops = {
        "Сумма операции с округлением": {"1111": -150, "2222": -50},
        "Кэшбэк": {"1111": 1.5, "2222": 0.5},
    }

    fake_top5 = {
        "Дата платежа": {0: "2024-06-01 10:00:00", 1: "2024-06-02 11:00:00"},
        "Сумма операции с округлением": {0: -10, 1: -5},
        "Категория": {0: "Кафе", 1: "Такси"},
        "Описание": {0: "Кофе", 1: "Поездка"},
    }

    fake_currency_rate = {"USD": 90.0, "EUR": 100.0}
    fake_stock_rate = {"AAPL": "123.45", "MSFT": "321.00"}

    # --- Мокаем все функции внутри src.views ---
    with patch("src.views.greeting", return_value=fake_greeting), \
         patch("src.views.read_file", return_value=fake_df), \
         patch("src.views.card_operations", return_value=fake_card_ops), \
         patch("src.views.top_5_operations", return_value=fake_top5), \
         patch("src.views.currency_rate", return_value=fake_currency_rate), \
         patch("src.views.stock_rate", return_value=fake_stock_rate):

        result = main("2024-06-01 12:00:00", file="fake.xlsx")
        parsed = json.loads(result)

    # --- Проверяем результат ---
    assert parsed["greeting"] == "Добрый день"

    assert parsed["cards"] == [
        {"last_digits": "1111", "total_spent": -150, "cashback": 1.5},
        {"last_digits": "2222", "total_spent": -50, "cashback": 0.5},
    ]

    assert parsed["top_transactions"] == [
        {"date": "2024-06-01 10:00:00", "amount": -10,
         "category": "Кафе", "description": "Кофе"},
        {"date": "2024-06-02 11:00:00", "amount": -5,
         "category": "Такси", "description": "Поездка"},
    ]

    assert parsed["currency_rates"] == [
        {"currency": "USD", "rate": 90.0},
        {"currency": "EUR", "rate": 100.0},
    ]

    assert parsed["stock_prices"] == [
        {"stock": "AAPL", "price": "123.45"},
        {"stock": "MSFT", "price": "321.00"},
    ]