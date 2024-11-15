import pandas as pd
from Lab_one import store, brands
from Lab_one.brands import group_map


df = pd.read_xml("dataset.xml")
df_anon = df.copy()

print("Оригинальный DataFrame:")
print(df.head(5))


def find_category(shop_name):
    for category, shops_dict in store.shops.items():
        if shop_name in shops_dict:
            return category
    return None


def anon_Store_Name():
    df_anon["Store_Name"] = df["Store_Name"].apply(find_category)


def anon_coordinat():
    df_anon["Координаты"] = "Санкт-Петербург"


def anon_Date_Time():
    df_anon["Date_Time"] = df["Date_Time"].apply(lambda x: x.split("-")[0])



def anon_category():
    df_anon["Category"] ="***"

def anon_brand():
    df_anon["Brand"] = "***"


def anon_Card_Number():
    sber = ['2202', '5469', '4276']
    t_bank = ['2200', '5489', '4277']
    vtb = ['2204', '5443', '4272']
    df_anon["Card_Number"] = df["Card_Number"].apply(
        lambda x: "Сбербанк" if x[:4] in sber else ("Т-банк" if x[:4] in t_bank else "ВТБ")
    )



def anon_Quantity():
    bins = [5, 30, 51]
    labels = [f'{bins[i]}-{bins[i + 1] - 1}' for i in range(len(bins) - 1)]
    df_anon['Quantity'] = pd.cut(df['Quantity'], bins=bins, labels=labels, include_lowest=True)



def anon_Cost():
    bins = [0,100000, 1000000, 10000000]
    labels = [f'{bins[i]}-{bins[i + 1] - 1}' for i in range(len(bins) - 1)]
    df_anon['Cost'] = pd.cut(df['Cost'], bins=bins, labels=labels, include_lowest=True)


def what_want():
    anon_store = int(input("Хотите обезличить названия магазинов? 1 - да 0 - нет: "))
    anon_coord = int(input("Хотите обезличить координаты? 1 - да 0 - нет: "))
    anon_date = int(input("Хотите обезличить дату и время? 1 - да 0 - нет: "))
    anon_categ = int(input("Хотите обезличить категории? 1 - да 0 - нет: "))
    anon_brands = int(input("Хотите обезличить бренды? 1 - да 0 - нет: "))
    anon_card = int(input("Хотите обезличить номера карт? 1 - да 0 - нет: "))
    anon_kolvo = int(input("Хотите обезличить количество товаров? 1 - да 0 - нет: "))
    anon_cost = int(input("Хотите обезличить стоимость? 1 - да 0 - нет: "))

    if anon_store == 1:
        anon_Store_Name()
    if anon_coord == 1:
        anon_coordinat()
    if anon_date == 1:
        anon_Date_Time()
    if anon_categ == 1:
        anon_category()
    if anon_brands == 1:
        anon_brand()
    if anon_card == 1:
        anon_Card_Number()
    if anon_kolvo == 1:
        anon_Quantity()
    if anon_cost == 1:
        anon_Cost()


what_want()
print("\nModified DataFrame:")
print(df_anon.head(5))
quasi_identifiers = ["Store_Name", "Координаты", "Date_Time","Quantity", "Card_Number","Cost", "Category"]#, "Cost"]


def calculate_k_anonymity(df, quasi_identifiers, n):
    group_counts = df.groupby(quasi_identifiers).size()
    k_values = sorted(group_counts)[:n]
    return k_values

n = 10
k_values = calculate_k_anonymity(df_anon, quasi_identifiers, n)
print(f"Первые {n} значений K-анонимности: {k_values}")


total_records = len(df_anon)
percentages = [(k / total_records) * 100 for k in k_values]
print("\nПроцентное соотношение первых K-анонимностей:")
print(percentages)
df_anon.to_xml('dataset_anon.xml', index=False, encoding='utf-8', root_name='purchases', row_name='purchase')