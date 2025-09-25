from typing import Dict

import pandas as pd
import datetime
import logging
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY_CURRENCY = os.getenv('API_KEY_CURRENCY')
API_KEY_STOCK = os.getenv('API_KEY_STOCK')


def read_file(file_name: str) -> pd.DataFrame:
    """Читаем файл Эксель и возвращаем датафрейм"""
    df = pd.read_excel(file_name)
    df["Номер карты"] = df["Номер карты"].replace("*","", regex=False)
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

# print(begin_of_month("2022-09-10 7:45:45"))

def card_operations(df: pd.DataFrame) -> Dict:
    """Формируем расходы и кешбэк по каждой карте"""
    expenses = df[(df["Сумма операции"]) < 0].copy()
    expenses["Кэшбэк"] = expenses["Сумма операции"] * -0.01
    new_df = expenses.groupby("Номер карты").agg({'Сумма операции с округлением': 'sum', 'Кэшбэк': 'sum'})
    return new_df.to_dict()



# df = read_file("data/operations.xlsx")
# old_dict = (card_operations(df))
# print(old_dict)
# print(type(old_dict))
#
# new_dict = {}
# new_dict["cards"] = old_dict['Сумма операции с округлением']
# print(new_dict)

def top_5_operations(df: pd.DataFrame) -> Dict:
    """Выводим топ-5 операций и оставляем только 4 столбца"""
    expenses = df[(df["Сумма операции"]) < 0].copy()
    top_df = expenses.sort_values(by='Сумма операции с округлением', ascending=False).head()
    finally_top = top_df.loc[:, ["Дата платежа", "Сумма операции с округлением", "Категория", "Описание"]]
    return finally_top.to_dict()

# df = read_file("data/operations.xlsx")
# print(top_5_operations(df))



def api_currency(currency: str) -> float:
    """Получаем курс валют через API"""
    url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"

    payload = {}
    headers= {
      "apikey": API_KEY_CURRENCY
    }
    response = requests.request("GET", url, headers=headers, data = payload)
    status_code = response.status_code
    result = response.text
    currencies = json.loads(result)
    currency_price = currencies["result"]
    return currency_price

# currency_rate = api_currency("USD")
# print(currency_rate)
# print(type(currency_rate))


def currency_rate(file: str) -> dict:
    """Формируем словарь курсов валют"""
    with open(file) as file:
        file_load = json.load(file)
        currencies = file_load['user_currencies']
        rate = {}
        for i in range(len(currencies)):
            rate[currencies[i]] = api_currency(currencies[i])
        return rate

# print(currency_rate("data/user_settings.json"))

def api_stock(stock: str) -> float:
    """Получаем курс валют через API"""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_STOCK}"
    response = requests.request("GET", url)
    status_code = response.status_code
    result = response.text
    stocks = json.loads(result)
    stock_price = stocks["Global Quote"]["05. price"]
    return stock_price

# print(api_stock("AAPL"))

def stock_rate(file: str) -> dict:
    """Формируем словарь курсов акций"""
    with open(file) as file:
        file_load = json.load(file)
        stocks = file_load['user_stocks']
        rate = {}
        for i in range(len(stocks)):
            rate[stocks[i]] = api_stock(stocks[i])
        return rate

# print(stock_rate("data/user_settings.json"))




