import requests
from utils.config import NEWS_API_KEY

def fetch_financial_news():
    """ Fetches the latest financial news from trusted sources. """
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [(article["title"], article["url"]) for article in articles]

    return []

if __name__ == "__main__":
    news = fetch_financial_news()
    for title, url in news:
        print(f"{title} - {url}")
