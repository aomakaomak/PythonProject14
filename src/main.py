import logging

from reports import last_3_months_operations
from services import benefit_categories
from utils import read_file
from views import main

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/reports.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main_func():
    """Функция вызова всего функционала на главной странице"""
    try:
        logging.info("Вызываем весь функционал")
        json_answer = main("2022-12-03 12:12:12")
        print(json_answer)

        df = read_file("data/operations.xlsx")
        the_best_categories = benefit_categories(df, 2021, 12)
        print(the_best_categories)

        last_operations = last_3_months_operations(df, "Супермаркеты", "25.01.2022 12:23:45")
        print(last_operations)
        return "Спасибо за ваш запрос"
    except Exception as e:
        logging.error(f"Возникла ошибка '{e}'")
        return f"Запрос выполнить не удалось. Ошибка '{e}'"


main_func()
