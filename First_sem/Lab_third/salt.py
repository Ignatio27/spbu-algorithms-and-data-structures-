f = open("phones.txt")
phones = []
for i in f.read().split():
    phones.append(int(i))

results = open("resulst.txt").read().split()
results= [int(i[-11:]) for i in results]
for k in results:
    counter = 0
    salt = k-phones[0]
    for v in results:
        if v-salt in phones:
            counter +=1
    if counter == len(phones):
        break
print("Соль равна:",salt)

