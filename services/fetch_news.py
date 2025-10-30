import requests
from config import NEWS_API_KEY
from services.db_manager import insert_article

def fetch_news(category="technology", country="us"):
    url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={NEWS_API_KEY}"
    res = requests.get(url).json()
    articles = res.get("articles", [])

    if len(articles) == 0:
        url = f"https://newsapi.org/v2/everything?q={category}&language=en&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        articles = res.get("articles", [])

    for item in articles:
        data = {
            "title": item.get("title"),
            "description": item.get("description"),
            "url": item.get("url"),
            "image": item.get("urlToImage"),
            "category": category
        }
        insert_article(data)
