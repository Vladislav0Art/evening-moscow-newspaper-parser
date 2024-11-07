import requests
from bs4 import BeautifulSoup
from typing import List, Union
from dataclasses import dataclass
import logging
import os
import csv
import json
import sys
import argparse


CINEMA_EXCERPT_LENGTH = 120


# urls = [
#     "https://electro.nekrasovka.ru/books/6173751/pages/4",
#     "https://electro.nekrasovka.ru/books/6173753/pages/4",
# ]


@dataclass
class Cinema:
    name: str
    word_breaks: List[int]

    def __init__(self, name: str, word_breaks: Union[List[int], None] = None):
        """
        Example of a word break indexing:
        Put a break at sep: 'my|word'
        Indexing:            01|2345 -> i = 1
        """
        if word_breaks is None:
            word_breaks = [i for i, _ in enumerate(name)]
        self.name = name
        self.word_breaks = word_breaks


# cinemas: List[Cinema] = [
#     Cinema(name="Метрополь"), # word_breaks=[2, 5, 6]
#     Cinema(name="Ударник"),
#     Cinema(name="Орион"),
# ]


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


def break_at(word: str, word_break: int, word_break_separator: str) -> str:
    return word[:word_break] + word_break_separator + word[word_break:]


def find_cinema(cinema: Cinema, text: str, word_break_separator: str) -> List[Entry]:
    entry_indicies: List[Entry] = []

    def word_present(word: str, text: str, start: int) -> bool:
        end = start + len(word)
        return text[start:end] == word

    for i in range(len(text)):
        if text[i] == cinema.name[0]:
            found = False
            word_break_index: Union[int, None] = None

            if word_present(cinema.name, text, i):
                found = True
            else:
                # Check if the word is present for all word breaks
                for break_index in cinema.word_breaks:
                    word = break_at(cinema.name, break_index, word_break_separator)
                    if word_present(word, text, i):
                        word_break_index = break_index
                        found = True
                        break

            if found:
                entry_indicies.append(Entry(start_index=i, word_break=word_break_index))

                if word_break_index is not None:
                    broken_cinema = break_at(cinema.name, word_break_index, word_break_separator)
                    logging.info(f"[Cinema]: Found '{broken_cinema}' at index {i}.")
                else:
                    logging.info(f"[Cinema]: Found '{cinema.name}' at index {i}.")

    return entry_indicies


def main(urls: List[str], cinemas: List[Cinema], filename_csv: str = 'result.csv'):
    logging.info("Creating a directory for the artifacts.")
    # Ensure the directory exists
    os.makedirs('artifact/urls', exist_ok=True)

    sep = '- '

    # print out cinema names and their breaks
    for c in cinemas:
        breaks_str = ', '.join(map(lambda i: f"'{break_at(word=c.name, word_break=i, word_break_separator=sep)}'", c.word_breaks))
        logging.info(f"Provided cinema: '{c.name}'; breaks: [{breaks_str}]")

    logging.info("=== Start collecting data from the URLs ===")

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
                    logging.error("Date not found.")
                    exit(1)
                else:
                    logging.info(f"Extracted date: {date}")

                os.makedirs(f'artifact/urls/{iteration}', exist_ok=True)

                html_filepath = f'artifact/urls/{iteration}/full-content.html'
                with open(html_filepath, 'w') as file:
                    logging.info(f"Writing the full content to a file at '{html_filepath}'.")
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

                    text_filepath = f'artifact/urls/{iteration}/text-content.txt'
                    with open(text_filepath, 'w') as file:
                        logging.info(f"Writing the text content from the target tag <pre> to a file at '{text_filepath}'.")
                        file.write(text)

                    for cinema in cinemas:
                        entry_indicies = find_cinema(cinema, text, word_break_separator=sep)
                        for entry in entry_indicies:
                            l = len(cinema.name)
                            if entry.word_break is not None:
                                broken_cinema_name = break_at(cinema.name, entry.word_break, word_break_separator=sep)
                                l = len(broken_cinema_name)

                            excerpt = text[(entry.start_index - CINEMA_EXCERPT_LENGTH):(entry.start_index + l)]

                            writer.writerow([cinema.name, date, excerpt, url])

                else:
                    logging.error("Text items not found!")
            else:
                logging.error("Failed to retrieve the page.")



if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Parse cinema information from URLs.')
        parser.add_argument('input_filepath', type=str, nargs='?', default='input.json', help="""
            Path to the input JSON file.
            The file format should be as follows:
            {
                "urls": ["url1", "url2"],
                "cinemas": ["cinema1", "cinema2"]
            }
            Default: 'input.json'
        """)

        args = parser.parse_args()

        # Read the parameters
        input_filepath = args.input_filepath

        logging.info(f"Reading the input file from '{input_filepath}'.")

        with open(input_filepath, 'r') as file:
            config = json.load(file)

        urls = config.get("urls", [])
        if len(urls) <= 0:
            logging.warning(f'No "urls" array provided at \'{input_filepath}\'.')

        cinema_names = config.get("cinemas", [])
        if len(cinema_names) <= 0:
            logging.warning(f'No "cinemas" array provided at \'{input_filepath}\'.')

        cinemas = [Cinema(name=name) for name in cinema_names]

        main(urls, cinemas)
    except Exception as e:
        logging.error(e)