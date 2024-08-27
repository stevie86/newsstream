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

import feedparser
from datetime import datetime
import logging
from src.language_detection import detect_language
from src.topic_extraction import extract_topics

logger = logging.getLogger('news_aggregator')

def process_news_item(item, source):
    description = getattr(item, 'description', '')
    language = detect_language(item.title + ' ' + description)
    topics = extract_topics(item.title + ' ' + description)
    
    logger.debug(f"Processing item: {item.title}, Source: {source}, Language: {language}, Topics: {topics}")
    
    pub_date = getattr(item, 'published', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'title': item.title,
        'link': item.link,
        'description': description,
        'pub_date': pub_date,
        'source': source,
        'language': language,
        'topics': topics,
        'last_updated': current_time
    }

def fetch_rss_feed(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries
    except Exception as e:
        logger.error(f"Error fetching RSS feed from {url}: {e}")
        return []

def fetch_and_store_news(conn, sources, insert_or_update_news_item):
    for source in sources:
        logger.info(f"Fetching news from: {source['name']}")
        entries = fetch_rss_feed(source['url'])
        logger.info(f"Found {len(entries)} entries")
        for entry in entries:
            try:
                processed_item = process_news_item(entry, source['name'])
                insert_or_update_news_item(conn, processed_item)
            except Exception as e:
                logger.error(f"Error processing entry from {source['name']}: {e}")
