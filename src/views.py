import json
import logging

from utils import card_operations, currency_rate, greeting, read_file, stock_rate, top_5_operations

logger = logging.getLogger("views")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/reports.log", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main(date_time: str, file="data/operations.xlsx") -> str:
    """Формируем json-ответ из функций в utils.py"""
    logger.info("Формируем json-ответ")
    greeting_ = greeting(date_time)
    data = read_file(file)
    oper = card_operations(data)
    cards = []
    for card in oper["Кэшбэк"]:
        cards.append(
            {
                "last_digits": card[-4:],
                "total_spent": oper["Сумма операции с округлением"][card],
                "cashback": oper["Кэшбэк"][card],
            }
        )

    top5 = top_5_operations(data)
    top_op = []
    for operation in top5["Дата платежа"]:
        top_op.append(
            {
                "date": top5["Дата платежа"][operation],
                "amount": top5["Сумма операции с округлением"][operation],
                "category": top5["Категория"][operation],
                "description": top5["Описание"][operation],
            }
        )

    cur_rate = currency_rate("data/user_settings.json")
    currencies_rates = []
    for currency in cur_rate:
        currencies_rates.append({"currency": currency, "rate": cur_rate[currency]})

    stock_r = stock_rate("data/user_settings.json")
    stock_rates = []
    for stock in stock_r:
        stock_rates.append({"stock": stock, "price": stock_r[stock]})

    return json.dumps(
        {
            "greeting": greeting_,
            "cards": cards,
            "top_transactions": top_op,
            "currency_rates": currencies_rates,
            "stock_prices": stock_rates,
        },
        ensure_ascii=False,
        indent=4,
    )


# print(main("2022-12-03 12:12:12"))
#
# main("2022-12-03 12:12:12")
