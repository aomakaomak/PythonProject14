import pandas as pd
import datetime
import logging
from typing import Union


def read_file(file_name: str) -> pd.DataFrame:
    """Читаем файл Эксель и возвращаем датафрейм"""
    df = pd.read_excel(file_name)
    return df

# print(read_file("data/operations.xlsx"))

def greeting(date_string: str) -> str:
    """Принимаем дату и время и возвращаем приветствие в зависимости от времени"""
    try:
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logging.error(f"Неверный формат даты: {date_string}. Ошибка: {e}")
        raise ValueError(f"Неверный формат даты: {date_string}. Ошибка: {e}") from e
    if 0 <= date_obj.hour <= 6:
        our_greeting = "Доброй ночи"
    elif 6 < date_obj.hour < 12:
        our_greeting = "Доброе утро"
    elif 12 <= date_obj.hour < 18:
        our_greeting = "Добрый день"
    else:
        our_greeting = "Добрый вечер"
    return our_greeting

# print(greeting("2022-09-10 7:45:45"))



def date_now(date_string: str) -> datetime.date:
    """Удаляем время из текущей даты, оставляем только дату"""
    try:
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logging.error(f"Неверный формат даты: {date_string}. Ошибка: {e}")
        raise ValueError(f"Неверный формат даты: {date_string}. Ошибка: {e}") from e
    date_now = date_obj.date()
    return date_now

# print(date_now("2022-09-10 7:45:45"))


def begin_of_month(date_string: str) -> datetime.date:
    """Возвращаем 1 число текущего месяца"""
    try:
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logging.error(f"Неверный формат даты: {date_string}. Ошибка: {e}")
        raise ValueError(f"Неверный формат даты: {date_string}. Ошибка: {e}") from e
    year = date_obj.year
    month = date_obj.month
    first_day = datetime.datetime(year, month, 1).date()

    return first_day

print(begin_of_month("2022-09-10 7:45:45"))

