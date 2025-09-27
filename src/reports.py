from time import strptime

import pandas as pd
from typing import Optional
from utils import read_file
import datetime
from dateutil.relativedelta import relativedelta
import json
import logging

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     filename='data/report.log',  # Запись логов в файл
#                     filemode='w')  # Перезапись файла при каждом запуске

logger = logging.getLogger("reports")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/reports.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def writer (func):

    def wrapper(*args, **kwargs):
        """Декоратор, который записывает результат функции в заранее определенный файл"""
        result = func(*args, **kwargs)
        with open("data/reports.txt", "w", encoding="utf-8", newline="") as file:
            json.dump(result, file, ensure_ascii=False, indent=4)
        return result

    return wrapper


def writer_with_param(file_path):
    """Декоратор, в параметр которого записывается имя файла для записи результата работы функции"""
    def wrapper(func):
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            return result
        return inner
    return wrapper



@writer_with_param("data/new_report.txt")
@writer
def last_3_months_operations(data: pd.DataFrame, category: str, ref_date: Optional[str] = None) -> dict:
    """
    Возвращает операции за последние 3 месяца до ref_date включительно.

    :param data: DataFrame с колонкой 'Дата операции'
    :param category: указываем нужную категорию
    :param ref_date: строка с датой, например '2021-12-31'
    :return: DataFrame с отфильтрованными операциями
    """
    # Преобразуем колонку к datetime (учитываем формат из Excel)
    try:
        logger.info(f"Выполняем запрос к датафрейму {data}")
        data = data.copy()

        data["Дата операции"] = pd.to_datetime(
            data["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
        )
        if ref_date is None or ref_date == "":
            ref_date = datetime.datetime.today()
        else:
            ref_date = pd.to_datetime(ref_date, dayfirst=True, errors="coerce")

        # Преобразуем аргумент ref_date в datetime
        ref_date = pd.to_datetime(ref_date, dayfirst=True)

        # Граница "3 месяца назад"
        start_date = ref_date - relativedelta(months=3)

        # Фильтрация
        logger.info("Выполняем фильтрацию")
        mask = (data["Дата операции"] > start_date) & (data["Дата операции"] <= ref_date)
        filtered_data = data.loc[mask, ["Дата операции", "Категория", "Сумма операции"]]
        spend_to_category = filtered_data.groupby("Категория", as_index=False).sum("Сумма операции")
        result = spend_to_category.loc[spend_to_category["Категория"] == category]
        result_new = {}
        if not result.empty:
            result_new[category] = float(result["Сумма операции"].iloc[0])
        return result_new
    except Exception as e:
        logger.error(f"Произошла ошибка '{e}")
        return {}


result = last_3_months_operations(read_file("data/operations.xlsx"), "Супермаркеты", "25.01.2022 12:23:45")
print(result)




