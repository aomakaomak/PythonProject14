import json
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import last_3_months_operations, writer
from src.reports import writer_with_param


def _sample_df():
    # Формат дат как в Excel: "%d.%m.%Y %H:%M:%S"
    return pd.DataFrame(
        {
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
                -1.0,  # исключено
                -2.0,  # включено
                -5.0,  # включено, но в другой категории
                -3.0,  # включено
                -4.0,  # исключено
            ],
        }
    )


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


def test_writer_writes_json_and_returns_result():
    payload = {"a": 1, "b": ["x", "y"]}

    @writer
    def make_payload():
        return payload

    m = mock_open()
    # Патчим builtin open, чтобы не писать на диск
    with patch("builtins.open", m) as mopen:
        result = make_payload()

    # 1) Возвращаемое значение не изменено
    assert result == payload

    # 2) Файл открыт корректно
    mopen.assert_called_once_with("data/reports.txt", "w", encoding="utf-8", newline="")

    # 3) В файл записан ожидаемый JSON (с ensure_ascii=False и indent=4)
    handle = m()
    written = "".join(call.args[0] for call in handle.write.call_args_list)
    assert written == json.dumps(payload, ensure_ascii=False, indent=4)


def test_writer_does_not_write_when_function_raises():
    @writer
    def boom():
        raise ValueError("fail inside function")

    m = mock_open()
    with patch("builtins.open", m) as mopen:
        with pytest.raises(ValueError):
            boom()

    # При исключении из целевой функции файл не должен открываться/писаться
    mopen.assert_not_called()


@pytest.mark.parametrize(
    "path",
    [
        "data/reports1.json",
        "out/custom.json",
    ],
)
def test_writer_with_param_writes_json_to_given_path_and_returns_result(path):
    payload = {"ok": True, "items": [1, 2, 3]}

    @writer_with_param(path)
    def make_payload():
        return payload

    m = mock_open()
    with patch("builtins.open", m) as mopen:
        result = make_payload()

    # 1) Возврат результата не меняется
    assert result == payload

    # 2) Открыт именно переданный путь, с правильными параметрами
    mopen.assert_called_once_with(path, "w", encoding="utf-8", newline="")

    # 3) В файл ушёл корректный форматированный JSON
    handle = m()
    written_text = "".join(call.args[0] for call in handle.write.call_args_list)
    assert written_text == json.dumps(payload, ensure_ascii=False, indent=4)


def test_writer_with_param_does_not_write_when_function_raises():
    path = "data/should_not_be_written.json"

    @writer_with_param(path)
    def boom():
        raise RuntimeError("bad things")

    m = mock_open()
    with patch("builtins.open", m) as mopen:
        with pytest.raises(RuntimeError):
            boom()

    # Если целевая функция упала — файла быть не должно
    mopen.assert_not_called()
