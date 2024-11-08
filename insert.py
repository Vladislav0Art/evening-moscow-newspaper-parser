import csv
import json

"""
Accepts a CSV file of the following format:
```
url,year,date
https://electro.nekrasovka.ru/books/6173751/pages/4,1953,Sep 1
https://electro.nekrasovka.ru/books/6173753/pages/4,1953,Sep 2
https://electro.nekrasovka.ru/books/6173755/pages/4,1953,Sep 3
```

And tranforms it into `input.json` file of the following format:
```
{
    "urls": [
        "https://electro.nekrasovka.ru/books/6173751/pages/4",
        "https://electro.nekrasovka.ru/books/6173753/pages/4",
        "https://electro.nekrasovka.ru/books/6173755/pages/4"
    ]
}
```
"""

with open('input.csv', 'r') as input, open('input.json') as file:
    reader = csv.reader(input)
    rows = list(reader)[1:]

    config = json.load(file)

    if "urls" not in config:
        config["urls"] = []

    for row in rows:
        url = row[0]
        print("Read the row:", row)
        config["urls"].append(url)

    with open('input.json', 'w') as output:
        json.dump(config, output, indent=4)