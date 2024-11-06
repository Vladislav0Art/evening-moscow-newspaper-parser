import requests
from bs4 import BeautifulSoup
import logging
import os

urls = [
    "https://electro.nekrasovka.ru/books/6173751/pages/4"
]

cinemas = [
    "Метрополь", "Ударник", "Орион",
]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s:\t%(message)s',
    handlers=[
        logging.FileHandler("script.log"),
        logging.StreamHandler()
    ]
)


def main(urls, cinemas):
    logging.info("Creating a directory for the artifacts.")
    # Ensure the directory exists
    os.makedirs('artifact', exist_ok=True)

    for iteration, url in enumerate(urls):
        logging.info(f"[Iteration {iteration}]: fetching URL {url}")
        response = requests.get(url)

        if response.status_code == 200:
            logging.info("Page retrieved successfully.")

            soup = BeautifulSoup(response.text, 'html.parser')

            with open(f'artifact/full-content-{iteration}.html', 'w') as file:
                logging.info("Writing the full content to a file.")
                file.write(soup.prettify())

            text_items = soup.findAll("pre")

            logging.info(f"Parsed {len(text_items)} text items.")

            if (len(text_items) > 1):
                logging.error(f"Too many text items found: 1 expected, got {len(text_items)}")
                exit(1)

            if len(text_items) > 0:
                lines = map(lambda line: line.strip(), text_items[0].get_text().splitlines())
                lines = list(filter(lambda line: any(cinema in line for cinema in cinemas), lines))
                logging.info(lines)
            else:
                logging.error("Text items not found!")
        else:
            logging.error("Failed to retrieve the page.")



if __name__ == "__main__":
    try:
        main(urls, cinemas)
    except Exception as e:
        logging.error(e)