import json
import requests

NEWSAPI_KEY = '4d6317c37ab54d2b9500c36ac0e2d150'
BASE_URL = 'https://newsapi.org/v2/top-headlines'

parameters = {
    'country': 'us',
    'category': 'technology',
    'pageSize': 5,
    'apiKey': '4d6317c37ab54d2b9500c36ac0e2d150',
}

response = requests.get(BASE_URL, params=parameters)

articles_list = []

if response.status_code == 200:
    news_data = response.json()
    if 'articles' in news_data:
        articles = news_data['articles']
        for article in articles:
            article_dict = {
                'source': article['source'],
                'author': article['author'],
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'urlToImage': article['urlToImage'],
                'publishedAt': article['publishedAt'],
                'content': article['content']
            }
            articles_list.append(article_dict)
else:
    print("Failed to fetch news data. Status code:", response.status_code)

# Write the articles list to demo.json
with open('demo.json', 'w') as f:
    json.dump(articles_list, f, indent=4)

print("Data written to demo.json")
