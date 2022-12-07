import urllib.request
import json
from cs50 import SQL
import re

db = SQL("sqlite:///api.db")

unwanted_instruments = [
    'viola',
    'cello',
    'bass',
    'oboe',
    'flute',
    'clarinet',
    'bassoon',
    'harp',
    'trumpet',
    'horn',
    'tuba',
    'trombone',
    'guitar',
    'wind instruments',
    'strings',
    'string instruments',
    'quartet',
    'continuo',
    'drums',
    'timpani',
    'percussion',
    'ensemble',
]

# Reading into list of links
with open('links.txt', 'r') as file:
    while True:
        url = file.readline()
        if not url:
            break

        # Api request, make data readable
        response = urllib.request.urlopen(url)
        text = response.read()
        data = json.loads(text)

        # If the composer doesn't have chamber works (violin solo/violin+piano works appear only under chamber title), ignore entry
        if data['status']['success'] == 'false':
            continue

        # insert composer data into database
        composer = data['composer']
        name = composer['name']
        fullname = composer['complete_name']

        # NB: api stores birth/death as yyyy-mm-dd, so I manually changed it into an int that only shows year
        birthyear = int(composer['birth'][0] + composer['birth'][1] + composer['birth'][2] + composer['birth'][3])

        # Living composers
        if not composer['death']:
            deathyear = 2099
        else:
            deathyear = int(composer['death'][0] + composer['death'][1] + composer['death'][2] + composer['death'][3])

        epoch = composer['epoch']
        db.execute("INSERT INTO composers(name, fullname, birthyear, deathyear, epoch) VALUES (?, ?, ?, ?, ?)", name, fullname, birthyear, deathyear, epoch)

        # Getting composer's ID:
        composer_id = db.execute("SELECT id FROM composers WHERE name = ?", name)[0]['id']

        # Store violin works in SQL
        works = data['works']
        for i in range(len(works)):
            title = works[i]['title']
            subtitle = works[i]['subtitle']

            # If not violin works
            if not re.search('violin', title, re.IGNORECASE) or re.search('violin', subtitle, re.IGNORECASE):
                continue

            # If more than one violin
            if re.search('violins', title, re.IGNORECASE):
                continue

            # If more than violin + piano
            unwanted_instrument = False
            for i in range(len(unwanted_instruments)):
                if re.search(unwanted_instruments[i], title, re.IGNORECASE) or re.search(unwanted_instruments[i], subtitle, re.IGNORECASE):
                    unwanted_instrument = True
                    break
            if unwanted_instrument:
                continue

            # Else, insert into sql
            name = (title + " " + subtitle).strip()
            if re.search('sonata', title, re.IGNORECASE):
                form = 'Sonata'
            elif re.search('partita', title, re.IGNORECASE) or re.search('suite', title, re.IGNORECASE):
                form = 'Suite'
            else:
                form = 'Misc.'

            db.execute("INSERT INTO works(name, form, composer_id) VALUES (?, ?, ?)", name, form, composer_id)

            # If solo work
            if re.search('solo violin', title, re.IGNORECASE) or re.search('violin solo', title, re.IGNORECASE):
                db.execute("UPDATE works SET solo = 1 WHERE name = ?", name)

        # If composer has no works associated with it, delete
        if len(db.execute("SELECT * FROM works WHERE composer_id = ?", composer_id)) == 0:
            db.execute("DELETE FROM composers WHERE id = ?", composer_id)