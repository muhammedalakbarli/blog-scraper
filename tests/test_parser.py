from scraper.parser import QuoteParser

def test_parser_returns_list():
    html = """
    <div class="quote">
        <span class="text">Test</span>
        <small class="author">Author</small>
    </div>
    """
    result = QuoteParser.parse(html)
    assert isinstance(result, list)