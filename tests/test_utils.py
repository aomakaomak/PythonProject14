import pytest
import datetime
import pandas as pd
import json
from unittest.mock import patch, Mock
from src.utils import greeting, begin_of_month, date_now, card_operations, read_file, top_5_operations, currency_rate, stock_rate, api_currency, api_stock


@pytest.mark.parametrize("date_str, expected", [
    ("2024-01-10 00:00:00", "Доброй ночи"),   # граница начала ночи
    ("2024-01-10 06:59:00", "Доброй ночи"),   # конец ночи
    ("2024-01-10 11:59:59", "Доброе утро"),   # конец утра
    ("2024-01-10 12:00:00", "Добрый день"),   # начало дня
    ("2024-01-10 17:59:59", "Добрый день"),   # конец дня
    ("2024-01-10 18:00:00", "Добрый вечер"),  # начало вечера
    ("2024-01-10 23:59:59", "Добрый вечер"),  # конец вечера
])
def test_greeting_valid_ranges(date_str, expected):
    assert greeting(date_str) == expected


@pytest.mark.parametrize("bad_date", [
    "2024/01/10 00:00:00",   # неверный формат с /
    "10-01-2024 00:00:00",   # день-месяц-год
    "not-a-date",            # произвольная строка
    "2024-13-01 00:00:00",   # месяц 13
])
def test_greeting_invalid_format_raises(bad_date):
    with pytest.raises(ValueError):
        greeting(bad_date)


@pytest.mark.parametrize("date_str, expected_date", [
    ("2024-01-10 00:00:00", datetime.date(2024, 1, 10)),   # ровно в полночь
    ("2024-07-15 09:10:11", datetime.date(2024, 7, 15)),   # обычное время
    ("1999-12-31 23:59:59", datetime.date(1999, 12, 31)),  # конец века :)
])
def test_date_now_returns_only_date(date_str, expected_date):
    result = date_now(date_str)
    assert isinstance(result, datetime.date)
    assert result == expected_date


@pytest.mark.parametrize("bad_date", [
    "2024/01/10 00:00:00",   # неверный формат с /
    "10-01-2024 00:00:00",   # формат день-месяц-год
    "not-a-date",            # произвольная строка
    "2024-13-01 00:00:00",   # несуществующий месяц
])
def test_date_now_invalid_format_raises(bad_date):
    with pytest.raises(ValueError):
        date_now(bad_date)


@pytest.mark.parametrize("date_str, expected", [
    ("2024-01-15 10:20:30", datetime.date(2024, 1, 1)),   # середина января
    ("2024-07-31 23:59:59", datetime.date(2024, 7, 1)),   # конец июля
    ("2020-02-29 12:00:00", datetime.date(2020, 2, 1)),   # високосный февраль
    ("1999-12-01 00:00:00", datetime.date(1999, 12, 1)),  # ровно первое декабря
])
def test_begin_of_month_returns_first_day(date_str, expected):
    result = begin_of_month(date_str)
    assert isinstance(result, datetime.date)
    assert result == expected


@pytest.mark.parametrize("bad_date", [
    "2024/01/15 10:20:30",   # неверный формат с /
    "15-01-2024 10:20:30",   # формат день-месяц-год
    "not-a-date",            # случайная строка
    "2024-13-01 00:00:00",   # месяц 13
])
def test_begin_of_month_invalid_format_raises(bad_date):
    with pytest.raises(ValueError):
        begin_of_month(bad_date)


@pytest.fixture
def df_operations():
    return pd.DataFrame({
        "Номер карты": ["1111", "1111", "2222", "3333"],
        "Сумма операции": [-100.0, 200.0, -50.0, -70.0],
        "Сумма операции с округлением": [-100, 200, -50, -70],
    })

def test_card_operations_calculates_sums_and_cashback(df_operations):
    result = card_operations(df_operations)

    # Проверяем ключи результата
    assert set(result.keys()) == {"Сумма операции с округлением", "Кэшбэк"}

    sums = result["Сумма операции с округлением"]
    cashback = result["Кэшбэк"]

    # Для карты 1111: только -100 идёт в расходы
    assert sums["1111"] == -100
    assert cashback["1111"] == pytest.approx(1.0)  # 1% от 100

    # Для карты 2222: -50
    assert sums["2222"] == -50
    assert cashback["2222"] == pytest.approx(0.5)

    # Для карты 3333: -70
    assert sums["3333"] == -70
    assert cashback["3333"] == pytest.approx(0.7)

def test_card_operations_no_expenses_returns_empty():
    df = pd.DataFrame({
        "Номер карты": ["1111", "2222"],
        "Сумма операции": [100.0, 200.0],  # только доходы
        "Сумма операции с округлением": [100, 200],
    })

    result = card_operations(df)
    # Нет расходов → пустой словарь у всех ключей
    assert result == {
        "Сумма операции с округлением": {},
        "Кэшбэк": {}
    }


@pytest.fixture
def df_for_top():
    # Смешанные операции: положительные (доходы) и отрицательные (расходы)
    # Важны значения "Сумма операции с округлением" — по ним идёт сортировка по убыванию
    return pd.DataFrame({
        "Номер карты": ["1111","1111","1111","2222","2222","3333","3333","3333","4444"],
        "Сумма операции": [ 500.0, -10.0, -50.0, -20.0, -5.0, -100.0, -30.0, -40.0, 200.0],
        "Сумма операции с округлением": [ 500,   -10,   -50,   -20,   -5,   -100,   -30,   -40,   200],
        "Дата платежа": [
            "2024-06-01 10:00:00","2024-06-02 11:00:00","2024-06-03 12:00:00",
            "2024-06-04 13:00:00","2024-06-05 14:00:00","2024-06-06 15:00:00",
            "2024-06-07 16:00:00","2024-06-08 17:00:00","2024-06-09 18:00:00",
        ],
        "Категория": ["Зачисление","Кафе","АЗС","Такси","Продукты","Перевод","Кино","Транспорт","Зачисление"],
        "Описание":  ["Пополнение","Кофе","Топливо","Поездка","Магазин","P2P","Билеты","Метро","Пополнение"],
    })


def test_top_5_operations_only_expenses_and_columns(df_for_top):
    res = top_5_operations(df_for_top)

    # Проверяем состав столбцов
    assert set(res.keys()) == {"Дата платежа", "Сумма операции с округлением", "Категория", "Описание"}

    # Извлекаем суммы (значения словаря могут быть неупорядоченными по индексам,
    # поэтому проверим через множество и длину)
    sums_dict = res["Сумма операции с округлением"]
    assert len(sums_dict) == 5  # не более 5 операций
    # Топ-5 по убыванию среди РАСХОДОВ (-5, -10, -20, -30, -40)
    assert set(sums_dict.values()) == {-5, -10, -20, -30, -40}

    # Убедимся, что положительные операции (500, 200) не попали
    assert 500 not in sums_dict.values()
    assert 200 not in sums_dict.values()


def test_top_5_operations_sorted_descending(df_for_top):
    res = top_5_operations(df_for_top)
    sums = list(res["Сумма операции с округлением"].values())
    # Проверяем именно порядок: по убыванию (наибольшее значение ближе к нулю)
    # Ожидаем: -5, -10, -20, -30, -40
    assert sums == sorted(sums, reverse=True)
    assert sums[0] == -5
    assert sums[-1] == -40


def test_top_5_operations_less_than_five_expenses():
    # Здесь только 3 расхода → функция должна вернуть именно 3 строки
    df = pd.DataFrame({
        "Номер карты": ["1111","2222","3333","4444"],
        "Сумма операции": [-1.0, 10.0, -2.0, -3.0],
        "Сумма операции с округлением": [-1, 10, -2, -3],
        "Дата платежа": ["2024-01-01 00:00:00","2024-01-02 00:00:00","2024-01-03 00:00:00","2024-01-04 00:00:00"],
        "Категория": ["Кафе","Зачисление","АЗС","Такси"],
        "Описание":  ["Кофе","Пополнение","Топливо","Поездка"],
    })
    res = top_5_operations(df)

    assert set(res.keys()) == {"Дата платежа", "Сумма операции с округлением", "Категория", "Описание"}
    # Должно быть 3 записи (только -1, -2, -3)
    assert len(res["Сумма операции с округлением"]) == 3
    assert set(res["Сумма операции с округлением"].values()) == {-1, -2, -3}


def test_api_currency_returns_parsed_result():
    fake_json = {"result": 92.34}

    with patch("src.utils.requests.request") as mock_request:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = json.dumps(fake_json)
        mock_request.return_value = mock_resp

        price = api_currency("USD")
        assert price == 92.34

        # Проверяем вызов
        assert mock_request.call_count == 1
        args, kwargs = mock_request.call_args

        # Позиционные аргументы: method и url
        assert args[0] == "GET"
        assert "from=USD" in args[1]
        assert "to=RUB" in args[1]

        # Именованные аргументы: headers и data
        assert "headers" in kwargs and "apikey" in kwargs["headers"]
        assert "data" in kwargs


def test_api_stock_returns_parsed_result():
    fake_json = {
        "Global Quote": {
            "05. price": "181.23"
        }
    }

    with patch("src.utils.requests.request") as mock_request:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = json.dumps(fake_json)
        mock_request.return_value = mock_resp

        # Вызов функции
        price = api_stock("AAPL")

        # Проверка возвращаемого результата
        assert price == "181.23"

        # Проверка вызова mock
        assert mock_request.call_count == 1
        args, kwargs = mock_request.call_args

        # Проверяем, что вызван метод GET и в URL есть symbol=AAPL
        assert args[0] == "GET"
        assert "symbol=AAPL" in args[1]
        assert "function=GLOBAL_QUOTE" in args[1]
        assert "apikey=" in args[1]


def test_currency_rate_reads_file_and_calls_api(tmp_path):
    # Создаём временный JSON-файл с настройками пользователя
    data = {"user_currencies": ["USD", "EUR"]}
    file_path = tmp_path / "user_settings.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    # Замокаем api_currency, чтобы оно возвращало фиксированные значения
    with patch("src.utils.api_currency", side_effect=lambda cur: {"USD": 90.0, "EUR": 100.0}[cur]) as mock_api:
        result = currency_rate(str(file_path))

        # Проверяем результат
        assert result == {"USD": 90.0, "EUR": 100.0}

        # Проверяем, что api_currency вызван для каждой валюты
        assert mock_api.call_count == 2
        mock_api.assert_any_call("USD")
        mock_api.assert_any_call("EUR")

def test_stock_rate_reads_file_and_calls_api(tmp_path):
    # Создаём временный JSON-файл с акциями пользователя
    data = {"user_stocks": ["AAPL", "MSFT"]}
    file_path = tmp_path / "user_settings.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    # Замокаем api_stock, чтобы он возвращал фиксированные значения
    with patch("src.utils.api_stock", side_effect=lambda s: {"AAPL": "123.45", "MSFT": "321.00"}[s]) as mock_api:
        result = stock_rate(str(file_path))

        # Проверяем результат
        assert result == {"AAPL": "123.45", "MSFT": "321.00"}

        # Проверяем количество вызовов и аргументы
        assert mock_api.call_count == 2
        mock_api.assert_any_call("AAPL")
        mock_api.assert_any_call("MSFT")


def test_read_file_handles_empty_excel(tmp_path):
    # Пустой датафрейм со всеми нужными столбцами
    df_empty = pd.DataFrame(columns=[
        "Номер карты", "Сумма операции", "Сумма операции с округлением",
        "Дата платежа", "Категория", "Описание"
    ])
    file_path = tmp_path / "empty.xlsx"
    df_empty.to_excel(file_path, index=False)

    df_out = read_file(str(file_path))

    # Пустота сохраняется, типы допустимы
    assert df_out.empty
    assert list(df_out.columns) == list(df_empty.columns)

