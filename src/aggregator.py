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

def detect_language(text):
    try:
        return dspy_detect_language(text)
    except Exception as e:
        try:
            return detect(text)
        except Exception as e:
            return 'unknown'

def extract_topic(text):
    try:
        return dspy_extract_topic(text)
    except Exception as e:
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
        'pub_date': item.get('published', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'source': source,
        'language': language,
        'topics': ','.join(topics),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def fetch_rss_feed(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries
    except Exception as e:
        print(f"Error fetching RSS feed from {url}: {e}")
        return []
