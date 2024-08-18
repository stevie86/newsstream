import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_rss_feed(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml-xml')  # Specify lxml for XML parsing
    items = soup.find_all('item')
    articles = []
    for item in items:
        article = {
            'title': item.title.text,
            'link': item.link.text,
            'description': item.description.text,
            'pubDate': item.pubDate.text
        }
        articles.append(article)
    return pd.DataFrame(articles)

def scrape_website(url, article_selector, title_selector, content_selector):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    for article in soup.select(article_selector):
        title = article.select_one(title_selector).text.strip()
        content = article.select_one(content_selector).text.strip()
        articles.append({'title': title, 'content': content})
    return pd.DataFrame(articles)
