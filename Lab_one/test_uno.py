import random
from datetime import datetime, timedelta
import store
import brands
import tovar
import time
import pandas as pd
ves_banks = [int(i) for i in input("Введите 3 веса для банков (Сбербанк, ВТБ, Т-Банк):  ").split()]
ves_cards = [int(i) for i in input("Введите 3 веса для платежных систем (Visa, MasterCard, МИР): ").split()]
while len(ves_cards)!=3 and len(ves_cards)!=3:
    print("Вы ввели неккоретное число весов!")
    ves_banks = [int(i) for i in input("Введите 3 веса для банков (Сбербанк, ВТБ, Т-Банк):  ").split()]
    ves_cards = [int(i) for i in input("Введите 3 веса для платежных систем (Visa, MasterCard, МИР): ").split()]
banks_1 = ["Сбербанк", "ВТБ", "Т-Банк"]
pay_sistem_1 = ["Visa", "MasterCard", "МИР"]

n_rows = int(input("Введите количество строк (число большее 50 000): "))
if n_rows< 50000:
    print("Вы ввели число меньшее 50 000, поэтому число строк будет равно 50 000")
    n_rows = 50000

def weighted_choice(choices, weights):
    total = sum(weights)
    rnd = random.uniform(0, total)
    upto = 0
    for choice, weight in zip(choices, weights):
        if upto + weight >= rnd:
            return choice
        upto += weight
    return choices[-1]

p = time.time()
def generate_random_date():
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    start_time = datetime.combine(random_date, datetime.min.time()) + timedelta(hours=10)
    end_time = datetime.combine(random_date, datetime.min.time()) + timedelta(hours=21)
    random_time = start_time + timedelta(seconds=random.randint(0, int((end_time - start_time).total_seconds())))
    return random_time


def generate_random_cost(q):
    if q == 3:
        return random.randint(35000, 100000)
    elif q == 2:
        return random.randint(6000, 35000)
    return random.randint(100, 6000)


def generate_random_card_number():
    pay_system = weighted_choice(pay_sistem_1,ves_cards)
    bank = weighted_choice(banks_1,ves_banks)
    card_format = '{fig1} {fig2} {fig3} {fig4}'

    if pay_system == 'МИР':
        figures = {
            'Сбербанк': '2202',
            'Т-Банк': '2200',
            'ВТБ': '2204'
        }.get(bank, '2206')
    elif pay_system == 'MasterCard':
        figures = {
            'Сбербанк': '5469',
            'Т-Банк': '5489',
            'ВТБ': '5443'
        }.get(bank, '5406')
    else:
        figures = {
            'Сбербанк': '4276',
            'Т-Банк': '4277',
            'ВТБ': '4272'
        }.get(bank, '4279')

    argz = {
        'fig1': figures,
        'fig2': str(random.randint(1000, 9999)),
        'fig3': str(random.randint(1000, 9999)),
        'fig4': str(random.randint(1000, 9999))
    }
    return card_format.format(**argz)


def generate_row():
    q = 0
    napr_store = random.choice(list(store.shops.keys()))
    shope = random.choice(list(store.shops[napr_store].keys()))
    date_time = generate_random_date().isoformat()
    latitude, longitude = random.choice(store.shops[napr_store][shope])
    category = random.choice(list(tovar.tovars[napr_store].keys()))

    if category in brands.low_price_category[napr_store].keys():
        q = 1
        brand = random.choice(list(brands.low_price_category[napr_store][category]))
    elif category in brands.medium_price_category[napr_store].keys():
        q = 2
        brand = random.choice(list(brands.medium_price_category[napr_store][category]))
    else:
        q = 3
        brand = random.choice(list(brands.high_price_category[napr_store][category]))

    card_number = generate_random_card_number()
    quantity = random.randint(5, 50)
    cost = generate_random_cost(q) * quantity

    return {
        "Название магазина": shope,
        "Координаты" :  (latitude,longitude),
        "Дата и время": date_time,
        "Категория": category,
        "Бренд": brand,
        "Номер карточки": card_number,
        "Количество товаров": quantity,
        "Стоимость": cost
    }


data = [generate_row() for _ in range(n_rows)]
df = pd.DataFrame(data)
df_renamed = df.rename(columns={
    "Название магазина": "Store_Name",
    "Дата и время": "Date_Time",
    "Широта": "Latitude",
    "Долгота": "Longitude",
    "Категория": "Category",
    "Бренд": "Brand",
    "Номер карточки": "Card_Number",
    "Количество товаров": "Quantity",
    "Стоимость": "Cost"
})
df_renamed.to_xml('dataset.xml', index=False, encoding='utf-8', root_name='purchases', row_name='purchase')
print("Время выполнения: ", time.time() - p)