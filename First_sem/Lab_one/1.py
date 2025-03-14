import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta
import store
import brands
import tovar
import time


class Store:
    def __init__(self, shops):
        self.shops = shops

    def get_random_shop(self):
        napr_store = random.choice(list(self.shops.keys()))
        shope = random.choice(list(self.shops[napr_store].keys()))
        latitude, longitude = random.choice(self.shops[napr_store][shope])
        return napr_store, shope, latitude, longitude


class Brands:
    def __init__(self, low_price_category, medium_price_category, high_price_category):
        self.low_price_category = low_price_category
        self.medium_price_category = medium_price_category
        self.high_price_category = high_price_category

    def get_random_brand(self, napr_store, category):
        if category in self.low_price_category[napr_store].keys():
            return random.choice(list(self.low_price_category[napr_store][category])), 1
        elif category in self.medium_price_category[napr_store].keys():
            return random.choice(list(self.medium_price_category[napr_store][category])), 2
        else:
            return random.choice(list(self.high_price_category[napr_store][category])), 3


class TransactionGenerator:
    def __init__(self, store, brands, tovars):
        self.store = store
        self.brands = brands
        self.tovars = tovars

    def generate_random_date(self):
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2024, 12, 31)
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        start_time = datetime.combine(random_date, datetime.min.time()) + timedelta(hours=10)
        end_time = datetime.combine(random_date, datetime.min.time()) + timedelta(hours=21)
        random_time = start_time + timedelta(seconds=random.randint(0, int((end_time - start_time).total_seconds())))
        return random_time

    def generate_random_cost(self, q):
        if q == 3:
            return random.randint(50000, 100000)
        elif q == 2:
            return random.randint(20000, 50000)
        return random.randint(1000, 20000)

    def generate_random_card_number(self):
        payment_system = random.choice(["Visa", "MasterCard", "МИР"])
        bank = random.choice(["Сбербанк", "ВТБ", "Т-Банк"])

        card_format = '{fig1} {fig2} {fig3} {fig4}'
        if payment_system == 'МИР':
            figures = {
                'Сбербанк': '2202',
                'Т-Банк': '2200',
                'ВТБ': '2204'
            }.get(bank, '2206')
        elif payment_system == 'MasterCard':
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

    def generate_row(self):
        q = 0
        napr_store, shope, latitude, longitude = self.store.get_random_shop()
        date_time = self.generate_random_date().isoformat()
        category = random.choice(list(self.tovars[napr_store].keys()))
        brand, q = self.brands.get_random_brand(napr_store, category)
        card_number = self.generate_random_card_number()
        quantity = random.randint(5, 50)
        cost = self.generate_random_cost(q) * quantity

        return {
            "Название магазина": shope,
            "Дата и время": date_time,
            "Широта": latitude,
            "Долгота": longitude,
            "Категория": category,
            "Бренд": brand,
            "Номер карточки": card_number,
            "Количество товаров": quantity,
            "Стоимость": cost
        }


store_instance = Store(store.shops)
brands_instance = Brands(brands.low_price_category, brands.medium_price_category, brands.high_price_category)
transaction_generator = TransactionGenerator(store_instance, brands_instance, tovar.tovars)

n_rows = 50000
start_time = time.time()

data = [transaction_generator.generate_row() for _ in range(n_rows)]

df = pd.DataFrame(data)

df.to_csv('dataset.csv', index=False)
print(f"Время выполнения: {time.time() - start_time} секунд")
