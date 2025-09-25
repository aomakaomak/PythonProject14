from time import strptime

import pandas as pd
from typing import Optional
from utils import read_file
import datetime
from dateutil.relativedelta import relativedelta


def last_3_months_operations(data: pd.DataFrame, category: str, ref_date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает операции за последние 3 месяца до ref_date включительно.

    :param data: DataFrame с колонкой 'Дата операции'
    :param category: указываем нужную категорию
    :param date: строка с датой, например '2021-12-31'
    :return: DataFrame с отфильтрованными операциями
    """
    # Преобразуем колонку к datetime (учитываем формат из Excel)
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
    mask = (data["Дата операции"] > start_date) & (data["Дата операции"] <= ref_date)
    filtered_data = data.loc[mask, ["Дата операции", "Категория", "Сумма операции"]]
    spend_to_category = filtered_data.groupby("Категория", as_index=False).sum("Сумма операции")
    result = spend_to_category.loc[spend_to_category["Категория"] == category]
    return result


# result = last_3_months_operations(read_file("data/operations.xlsx"), "Супермаркеты", "25.01.2022 12:23:45")
# print(result)




