import datetime
import pandas as pd
import json
import logging

from utils import read_file


logger = logging.getLogger("services")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/reports.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def benefit_categories(data: pd.DataFrame, year: int, month: int) -> str:
    """Принимаем месяц и год и выводим сколько кэшбэка заработано по каждой категории"""
    try:
        logger.info("Рассчитываем категории")
        filtred_data = data.loc[:, ["Дата операции", "Категория", "Кэшбэк"]]
        dt = pd.to_datetime(filtred_data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtred_data_per_date = filtred_data.loc[
            (dt.dt.year == year) & (dt.dt.month == month)
        ]
        benefit_group = filtred_data_per_date.groupby("Категория").sum("Кэшбэк").to_dict()
        result_dict = benefit_group["Кэшбэк"]
        result_json = json.dumps(result_dict, ensure_ascii=False, indent=4)
        return result_json
    except Exception as e:
        logger.error(f"Возникла ошибка '{e}'")
        return ""

# df = read_file("data/operations.xlsx")
# result = benefit_categories(df, 2021, 12)
# print(result)
# print(type(result))
