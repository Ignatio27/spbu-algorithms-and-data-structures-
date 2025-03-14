import csv


with open("resulst.txt") as f:
    phones = [int(phone[-11:]) for phone in f.read().split()]
    #hash_1 = [phone[:33] for phone in f.read().split()]

salt = 56998744

corrected_numbers = [phone - salt for phone in phones]

with open('corrected_numbers.csv', 'w', newline='') as csvfile:
    fieldnames = ['False phone', 'Corrected Phone','salt']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for original, corrected in zip(phones, corrected_numbers):
        writer.writerow({'False phone': original, 'Corrected Phone': corrected,'salt':56998744})

print("Новый CSV файл с правильными номерами создан: corrected_numbers.csv")
