import datetime
import pandas as pd
import json

from utils import read_file


def benefit_categories(data: pd.DataFrame, year: int, month: int) -> str:
    """Принимаем месяц и год и выводим сколько кэшбэка заработано по каждой категории"""
    filtred_data = data.loc[:, ["Дата операции", "Категория", "Кэшбэк"]]
    dt = pd.to_datetime(filtred_data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtred_data_per_date = filtred_data.loc[
        (dt.dt.year == year) & (dt.dt.month == month)
    ]
    benefit_group = filtred_data_per_date.groupby("Категория").sum("Кэшбэк").to_dict()
    result_dict = benefit_group["Кэшбэк"]
    result_json = json.dumps(result_dict, ensure_ascii=False, indent=4)
    return result_json

# df = read_file("data/operations.xlsx")
# result = benefit_categories(df, 2021, 12)
# print(result)
# print(type(result))
