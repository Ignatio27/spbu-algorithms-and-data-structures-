import random
from datetime import datetime, timedelta
import store
import brands
import tovar
import time
import pandas as pd

# Вводим вероятности для банков и платежных систем
ves_banks = [int(i) for i in input("Введите 3 вероятности для банков: ").split()]
ves_cards = [int(i) for i in input("Введите 3 вероятности для платежных систем: ").split()]

banks_1 = ["Sberbank", "VTB", "T-Bank"]  # Переименовали для удобства в XML
pay_sistem_1 = ["Visa", "MasterCard", "MIR"]

def weighted_choice(choices, weights):
    total = sum(weights)
    rnd = random.uniform(0, total)
    upto = 0
    for choice, weight in zip(choices, weights):
        if upto + weight >= rnd:
            return choice
        upto += weight
    return choices[-1]

n_rows = 50000
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
    pay_system = weighted_choice(pay_sistem_1, ves_cards)
    bank = weighted_choice(banks_1, ves_banks)
    card_format = '{fig1} {fig2} {fig3} {fig4}'

    if pay_system == 'MIR':
        figures = {
            'Sberbank': '2202',
            'T-Bank': '2200',
            'VTB': '2204'
        }.get(bank, '2206')
    elif pay_system == 'MasterCard':
        figures = {
            'Sberbank': '5469',
            'T-Bank': '5489',
            'VTB': '5443'
        }.get(bank, '5406')
    else:
        figures = {
            'Sberbank': '4276',
            'T-Bank': '4277',
            'VTB': '4272'
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
        "Store_Name": shope,  # Переименовали колонку
        "Coordinates": f"{latitude},{longitude}",  # Переименовали и форматировали координаты
        "Date_Time": date_time,  # Переименовали колонку
        "Category": category,  # Переименовали колонку
        "Brand": brand,  # Переименовали колонку
        "Card_Number": card_number,  # Переименовали колонку
        "Quantity": quantity,  # Переименовали колонку
        "Cost": cost  # Переименовали колонку
    }

# Генерация данных
data = [generate_row() for _ in range(n_rows)]
df = pd.DataFrame(data)

# Сохранение DataFrame в формате XML
df.to_xml('dataset.xml', index=False, encoding='utf-8', root_name='purchases', row_name='purchase')

print("Время выполнения: ", time.time() - p)
