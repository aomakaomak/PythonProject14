

from utils import read_file


def benefit_categories(data, year, month):
    filtred_per_date = data.to_dict()
    return filtred_per_date

df = read_file("data/operations.xlsx")
result = benefit_categories(df, 2018, 11)
print(result)