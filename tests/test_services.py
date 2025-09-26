import pandas as pd
import json
import pytest
from src.services import benefit_categories


def test_benefit_categories_returns_correct_json():
    # Подготовка входных данных
    df = pd.DataFrame({
        "Дата операции": [
            "01.06.2024 12:00:00", "05.06.2024 15:00:00", "15.07.2024 10:00:00"
        ],
        "Категория": ["Продукты", "АЗС", "Продукты"],
        "Кэшбэк": [10.0, 5.0, 20.0]
    })

    # Вызываем функцию за июнь 2024
    result_json = benefit_categories(df, 2024, 6)
    parsed = json.loads(result_json)

    # Проверяем, что сгруппировано правильно
    assert parsed == {
        "Продукты": 10.0,
        "АЗС": 5.0,
    }


def test_benefit_categories_returns_empty_when_no_data():
    # Подготовка: данные только за май
    df = pd.DataFrame({
        "Дата операции": ["01.05.2024 12:00:00"],
        "Категория": ["Продукты"],
        "Кэшбэк": [10.0]
    })

    # Запрос за июнь — данных нет
    result_json = benefit_categories(df, 2024, 6)
    parsed = json.loads(result_json)

    assert parsed == {}  # пустой словарь


@pytest.mark.parametrize("month,expected", [
    (6, {"Продукты": 10.0, "АЗС": 5.0}),
    (7, {"Продукты": 20.0}),
])
def test_benefit_categories_parametrized(month, expected):
    # Подготовка
    df = pd.DataFrame({
        "Дата операции": [
            "01.06.2024 12:00:00", "05.06.2024 15:00:00", "15.07.2024 10:00:00"
        ],
        "Категория": ["Продукты", "АЗС", "Продукты"],
        "Кэшбэк": [10.0, 5.0, 20.0]
    })

    result_json = benefit_categories(df, 2024, month)
    parsed = json.loads(result_json)

    assert parsed == expected