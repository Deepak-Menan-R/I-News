import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime, timedelta

# NewsAPI configuration
NEWSAPI_KEY = '4d6317c37ab54d2b9500c36ac0e2d150'
NEWSAPI_URL = 'https://newsapi.org/v2/top-headlines'

# MongoDB configuration
MONGODB_URL = 'mongodb://localhost:27017/'
DATABASE_NAME = 'apistory'
COLLECTION_NAME = 'apistorypoints'

def fetch_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_content = soup.find('div', class_='article-content')  
            if article_content:
                return article_content.text.strip()
            else:
                return None
        else:
            return None
    except Exception as e:
        return None

def fetch_news_from_api(category, country):
    try:
        params = {
            'country': country,
            'category': category,
            'apiKey': NEWSAPI_KEY
        }
        response = requests.get(NEWSAPI_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            for article in articles:
                article['content'] = fetch_article_content(article['url'])
                article['timestamp'] = datetime.utcnow()  
            return articles
        else:
            print(f"Failed to fetch news from NewsAPI for category {category} and country {country}.")
            return []
    except Exception as e:
        print(f"Error fetching news from NewsAPI: {e}")
        return []

def store_news_in_mongodb(news_articles, category, country):
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    for article in news_articles:
        article['category'] = category
        article['country'] = country
        collection.insert_one(article)

def get_latest_news_timestamp():
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    latest_article = collection.find_one(sort=[("timestamp", -1)])
    if latest_article:
        return latest_article['timestamp']
    else:
        return datetime.utcnow() - timedelta(days=1)  

def main():
    categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology', 'general', 'politics', 'world', 'finance', 'environment', 'education', 'travel', 'food', 'arts', 'culture', 'lifestyle', 'opinion', 'weather', 'music', 'fashion', 'automobile']
    countries = ['us', 'in', 'gb', 'au', 'ca', 'fr', 'de', 'jp', 'it', 'br']  # Add more countries as needed
    latest_timestamp = get_latest_news_timestamp()
    for category in categories:
        for country in countries:
            news_articles = fetch_news_from_api(category, country)
            new_articles = [article for article in news_articles if article['timestamp'] > latest_timestamp]
            if new_articles:
                store_news_in_mongodb(new_articles, category, country)
                print(f"{len(new_articles)} new articles stored in MongoDB for category {category} and country {country}.")
            else:
                print(f"No new articles found for category {category} and country {country}.")

def schedule_updates():
    # Schedule updates to run every 30 minutes
    schedule.every(2).minutes.do(main)
    
    # Run the scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_updates()
