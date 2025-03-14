import pandas as pd

df = pd.read_excel('scoring_data_v.1.9.xlsx', sheet_name='A2', header=None)

df.loc[1:50001, 0].to_csv('hashes.txt', index=False, header=False)
df.loc[1:5, 2].to_csv('phones.txt', index=False, header=False)
print("Файлы hashes.txt и phones.txt были успешно созданы")