import hashlib
with open("corrected_phones.txt", "w") as f:
    file = open('corrected_numbers.csv')
    file = file.read().split('\n')[1:]
    print(file[0])
    file = file[:len(file)-1]
    fi = [i.split(',')[1] for i in file]
    for h in fi:
        f.write(h + "\n")

def create_hashes(file_path):
    sha1_hashes = []
    sha256_hashes = []

    with open(file_path, "r") as f:
        for line in f:
            phone_number = line.strip()+'125'

            sha1_hash = hashlib.sha1(phone_number.encode()).hexdigest()
            sha1_hashes.append(sha1_hash)


            sha256_hash = hashlib.sha256(phone_number.encode()).hexdigest()
            sha256_hashes.append(sha256_hash)

    return sha1_hashes, sha256_hashes


file_path = "corrected_phones.txt"
sha1_hashes, sha256_hashes = create_hashes(file_path)

with open("sha1_hashes_1.txt", "w") as f:
    for h in sha1_hashes:
        f.write(h + "\n")

with open("sha256_hashes.txt", "w") as f:
    for h in sha256_hashes:
        f.write(h + "\n")

print("Хеши успешно созданы и записаны в sha1_hashes.txt и sha256_hashes.txt")