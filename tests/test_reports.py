import pandas as pd
import pytest
from src.reports import last_3_months_operations

def _sample_df():
    # Формат дат как в Excel: "%d.%m.%Y %H:%M:%S"
    return pd.DataFrame({
        "Дата операции": [
            "15.05.2024 00:00:00",  # ровно на границе старта окна -> ИСКЛЮЧЕНО (>)
            "16.05.2024 00:00:00",  # внутри окна -> ВКЛЮЧЕНО
            "01.06.2024 12:00:00",  # внутри окна -> ВКЛЮЧЕНО
            "15.08.2024 00:00:00",  # ровно на верхней границе -> ВКЛЮЧЕНО (≤)
            "16.08.2024 00:00:00",  # за верхней границей -> ИСКЛЮЧЕНО
        ],
        "Категория": [
            "Продукты",
            "Продукты",
            "АЗС",
            "Продукты",
            "Продукты",
        ],
        "Сумма операции": [
            -1.0,   # исключено
            -2.0,   # включено
            -5.0,   # включено, но в другой категории
            -3.0,   # включено
            -4.0,   # исключено
        ],
    })


def test_last_3_months_operations_filters_and_sums_by_category():
    df = _sample_df()
    # Окно: ref_date = 15.08.2024 00:00:00
    # start_date = 15.05.2024 00:00:00
    # правило: (date > start) & (date <= ref)
    out = last_3_months_operations(df, category="Продукты", ref_date="2024-08-15")
    # Должно войти: 16.05 (-2.0) и 15.08 (-3.0) => сумма -5.0
    assert out == {"Продукты": -5.0}


def test_last_3_months_operations_ref_date_dayfirst_parsing():
    df = _sample_df()
    # Тот же день, но строка в формате с dayfirst=True
    out = last_3_months_operations(df, category="Продукты", ref_date="15-08-2024")
    assert out == {"Продукты": -5.0}


def test_last_3_months_operations_no_ref_date_uses_today(monkeypatch):
    df = _sample_df()

    # Зафиксируем "сегодня" как 15.08.2024 00:00:00
    import datetime as _dt
    class FixedDateTime(_dt.datetime):
        @classmethod
        def today(cls):
            return cls(2024, 8, 15, 0, 0, 0)
    # Патчим именно класс datetime в модуле src.utils
    monkeypatch.setattr("src.utils.datetime.datetime", FixedDateTime)

    out = last_3_months_operations(df, category="Продукты", ref_date=None)
    assert out == {"Продукты": -5.0}


def test_last_3_months_operations_unknown_category_returns_empty():
    df = _sample_df()
    out = last_3_months_operations(df, category="Кафе", ref_date="2024-08-15")
    assert out == {}
