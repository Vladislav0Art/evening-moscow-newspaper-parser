import requests
from bs4 import BeautifulSoup

# Fetch the page
url = "https://electro.nekrasovka.ru/books/6173751/pages/4"
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the content inside a specific tag
    content_div = soup.findAll("pre") # sc-1yixj9f-3 btFrcD

    with open('content.html', 'w') as file:
        file.write(soup.prettify())

    if content_div:
        print(content_div)
    else:
        print("Content not found!")
else:
    print("Failed to retrieve the page.")