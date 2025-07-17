# news_fetcher.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

def get_climate_news():

    params = {
        "q": "climate change OR global warming OR carbon emissions OR renewable energy OR green energy OR deforestation OR climate crisis OR air pollution OR eco-friendly OR climate policy OR heatwaves OR climate innovation",
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": API_KEY,
        "pageSize": 100
    }

    try:
        response = requests.get(NEWS_API_URL, params=params)
        data = response.json()

        articles = []
        if data["status"] == "ok":
            for article in data["articles"]:
                articles.append({
                    "title": article["title"],
                    "description": article["description"],
                    "url": article["url"],
                    "urlToImage": article.get("urlToImage"), 
                    "source": article["source"],
                    "publishedAt": article["publishedAt"],
                    "author": article["author"]
                })
        return articles

    except Exception as e:
        print("Error fetching news:", e)
        return [{"title": "News fetch failed", "description": str(e), "url": "#"}]
