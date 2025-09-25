import json

from utils import greeting, card_operations, read_file, top_5_operations


def main(date_time: str, file="data/operations.xlsx") -> str:
    greeting_ = greeting(date_time)
    data = read_file(file)
    oper = card_operations(data)
    cards = []
    for card in oper["Кэшбэк"]:
        cards.append({
            "last_digits": card[-4:],
            "total_spent": oper["Сумма операции с округлением"][card],
            "cashback": oper["Кэшбэк"][card]
        })
    # print(greeting_)
    # print(cards)

    top5 = top_5_operations(data)
    top_op = []
    for operation in top5["Дата платежа"]:
        top_op.append({
            "date": top5["Дата платежа"][operation],
            "amount": top5["Сумма операции с округлением"][operation],
            "category": top5["Категория"][operation],
            "description": top5["Описание"][operation]
        })

    return json.dumps({
        "greeting": greeting_,
        "cards": cards,
        "top_transactions": top_op
    }, ensure_ascii=False, indent=4)


print(main("2022-12-03 12:12:12"))
