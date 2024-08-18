import requests
from bs4 import BeautifulSoup
import pandas as pd
import feedparser
from datetime import datetime
from langdetect import detect
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import nltk
from dspy_utils import dspy_extract_topic, dspy_detect_language

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        article = {
            'title': entry.title,
            'link': entry.link,
            'description': entry.get('description', ''),
            'pubDate': entry.get('published', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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

def detect_language(text):
    try:
        return dspy_detect_language(text)
    except:
        try:
            return detect(text)
        except:
            return 'unknown'

def extract_topic(text):
    try:
        return dspy_extract_topic(text)
    except:
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
        word_freq = Counter(tokens)
        return word_freq.most_common(1)[0][0] if word_freq else 'unknown'

def process_news_item(item, source):
    description = item.get('description', '')
    language = detect_language(item['title'] + ' ' + description)
    topics = [extract_topic(item['title'] + ' ' + description)]
    
    return {
        'title': item['title'],
        'link': item['link'],
        'description': description,
        'pub_date': item['pubDate'],
        'source': source,
        'language': language,
        'topics': ','.join(topics),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
