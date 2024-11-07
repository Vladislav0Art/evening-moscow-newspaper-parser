import requests
from bs4 import BeautifulSoup
from typing import List, Union
from dataclasses import dataclass
import logging
import os
import csv

urls = [
    "https://electro.nekrasovka.ru/books/6173751/pages/4",
    "https://electro.nekrasovka.ru/books/6173753/pages/4",
]


@dataclass
class Cinema:
    name: str
    word_breaks: List[int]

    def __init__(self, name: str, word_breaks: Union[List[int], None] = None):
        # 'my|word'
        #  01|23456 -> i = 1
        if word_breaks is None:
            word_breaks = [i for i, _ in enumerate(name)] + [len(name)]
        self.name = name
        self.word_breaks = word_breaks


cinemas: List[Cinema] = [
    Cinema(name="Метрополь", word_breaks=[2, 4, 6]),
    Cinema(name="Ударник"),
    Cinema(name="Орион"),
]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s:\t%(message)s',
    handlers=[
        logging.FileHandler("script.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class Entry:
    start_index: int
    word_break: Union[int, None] = None


def find_cinema(cinema: Cinema, text: str, word_break_separator: str) -> List[Entry]:
    entry_indicies: List[Entry] = []

    def word_present(word: str, text: str, start: int) -> bool:
        end = start + len(word)
        return text[start:end] == word

    def break_at(word: str, word_break: int) -> str:
        return word[:word_break] + word_break_separator + word[word_break:]

    for i in range(len(text)):
        if text[i] == cinema.name[0]:
            found = False
            word_break_index: Union[int, None] = None

            if word_present(cinema.name, text, i):
                found = True
            else:
                # Check if the word is present for all word breaks
                for break_index in cinema.word_breaks:
                    word = break_at(cinema.name, break_index)
                    if word_present(word, text, i):
                        word_break_index = break_index
                        found = True
                        break

            if found:
                entry_indicies.append(Entry(start_index=i, word_break=word_break_index))

                if word_break_index is not None:
                    logging.info(f"Found {break_at(cinema.name, word_break_index)} at index {i}.")
                else:
                    logging.info(f"Found {cinema.name} at index {i}.")

    return entry_indicies


def main(urls: List[str], cinemas: List[Cinema], filename_csv: str = 'result.csv'):
    logging.info("Creating a directory for the artifacts.")
    # Ensure the directory exists
    os.makedirs('artifact/urls', exist_ok=True)

    with open(f"artifact/{filename_csv}", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['cinema', 'date', 'title_excerpt', 'url'])

        for iteration, url in enumerate(urls):
            logging.info(f"[Iteration {iteration}]: fetching URL {url}")
            response = requests.get(url)

            if response.status_code == 200:
                logging.info("Page retrieved successfully.")

                soup = BeautifulSoup(response.text, 'html.parser')

                date = soup.find('div', class_='sc-flyd3z-5 bJFbFd').find('a').text.strip()

                if date is None:
                    logging.info("Date not found.")
                else:
                    logging.info(f"Extracted date: {date}")

                with open(f'artifact/urls/full-content-{iteration}.html', 'w') as file:
                    logging.info("Writing the full content to a file.")
                    file.write(soup.prettify())

                text_items = soup.findAll("pre")

                logging.info(f"Parsed {len(text_items)} text items.")

                if (len(text_items) > 1):
                    logging.error(f"Too many text items found: 1 expected, got {len(text_items)}")
                    exit(1)

                if len(text_items) > 0:
                    # lines = map(lambda line: line.strip(), text_items[0].get_text().splitlines())
                    # lines = list(filter(lambda line: any(cinema in line for cinema in cinemas), lines))
                    # logging.info(lines)
                    text = text_items[0].get_text().replace('\n', ' ')
                    logging.info(text)

                    for cinema in cinemas:
                        entry_indicies = find_cinema(cinema, text, word_break_separator='- ')

                else:
                    logging.error("Text items not found!")
            else:
                logging.error("Failed to retrieve the page.")



if __name__ == "__main__":
    try:
        main(urls, cinemas)
    except Exception as e:
        logging.error(e)