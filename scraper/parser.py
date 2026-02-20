from bs4 import BeautifulSoup


class QuoteParser:
    @staticmethod
    def parse(html: str):
        soup = BeautifulSoup(html, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        results = []

        for quote in quotes:
            text_el = quote.find("span", class_="text")
            author_el = quote.find("small", class_="author")

            if not text_el or not author_el:
                continue

            results.append({
                "text": text_el.get_text(strip=True),
                "author": author_el.get_text(strip=True),
                "tags": ", ".join(tag.text for tag in quote.find_all("a", class_="tag"))
            })

        return results