import csv
import json

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