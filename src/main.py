from views import main
from services import benefit_categories
from reports import last_3_months_operations
from utils import read_file


def main_func():
    json_answer = main("2022-12-03 12:12:12")
    print(json_answer)

    df = read_file("data/operations.xlsx")
    the_best_categories = benefit_categories(df, 2021, 12)
    print(the_best_categories)

    last_operations = last_3_months_operations(df, "Супермаркеты", "25.01.2022 12:23:45")
    print(last_operations)
    return "Спасибо за ваш запрос"

print(main_func())




