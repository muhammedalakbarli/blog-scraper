from scraper.client import ScraperClient
from scraper.parser import QuoteParser
from scraper.exporter import CSVExporter

def run(limit=20):
    client = ScraperClient()
    collected = []
    page = 1

    while len(collected) < limit:
        html = client.fetch_page(page)
        parsed = QuoteParser.parse(html)

        for item in parsed:
            collected.append(item)
            if len(collected) >= limit:
                break

        page += 1

    CSVExporter.export(collected)
    print(f"Successfully exported {len(collected)} records.")


if __name__ == "__main__":
    run()