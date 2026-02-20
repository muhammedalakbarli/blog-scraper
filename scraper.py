import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://quotes.toscrape.com"

def scrape_quotes(limit=20):
    quotes_data = []
    page = 1

    while len(quotes_data) < limit:
        url = f"{BASE_URL}/page/{page}/"
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        for quote in quotes:
            text = quote.find("span", class_="text").text
            author = quote.find("small", class_="author").text
            tags = [tag.text for tag in quote.find_all("a", class_="tag")]

            quotes_data.append({
                "text": text,
                "author": author,
                "tags": ", ".join(tags)
            })

            if len(quotes_data) >= limit:
                break

        page += 1

    return quotes_data


def export_to_csv(data, filename="posts.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved {len(data)} records to {filename}")


if __name__ == "__main__":
    data = scrape_quotes(limit=20)
    export_to_csv(data)