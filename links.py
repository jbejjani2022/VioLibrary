"""Get .txt file with all the queries necessary"""

with open('links.txt', 'a') as file:
    for i in range(1, 221):  # There are 220 composers in the database
        i = str(i)
        print("https://api.openopus.org/work/list/composer/" + i + "/genre/Chamber.json", file=file)