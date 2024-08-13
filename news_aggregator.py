import json
import sqlite3
import feedparser
from datetime import datetime
import time
from langdetect import detect
from newspaper import Article
import nltk
from icecream import ic

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# Configure icecream
ic.configureOutput(prefix='DEBUG | ')

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def create_table(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS news_items
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     title TEXT,
                     link TEXT UNIQUE,
                     description TEXT,
                     pub_date TEXT,
                     source TEXT,
                     language TEXT,
                     topic TEXT)''')

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'unknown'

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

def extract_topic(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # Count word frequencies
    word_freq = Counter(tokens)
    
    # Return the most common word as the topic
    return word_freq.most_common(1)[0][0] if word_freq else 'unknown'

def insert_news_item(conn, item, source):
    try:
        description = getattr(item, 'description', '')
        language = detect_language(item.title + ' ' + description)
        topic = extract_topic(item.title + ' ' + description)
        
        ic(item.title, source, language, topic)
        
        conn.execute('''INSERT INTO news_items (title, link, description, pub_date, source, language, topic)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (item.title, item.link, description,
                      item.published, source, language, topic))
        conn.commit()
    except sqlite3.IntegrityError:
        ic(f"Skipping duplicate entry: {item.title}")
    except AttributeError as e:
        ic(f"Error processing item: {e}")
        ic(f"Item attributes: {vars(item)}")

def fetch_and_store_news(conn, sources):
    for source in sources:
        ic(f"Fetching news from: {source['name']}")
        feed = feedparser.parse(source['url'])
        ic(f"Found {len(feed.entries)} entries")
        for entry in feed.entries:
            insert_news_item(conn, entry, source['name'])

def main():
    config = load_config('config.json')
    db_path = config['database_path']
    sources = config['sources']
    update_interval = config['update_interval']

    ic(f"Database path: {db_path}")
    ic(f"Number of sources: {len(sources)}")
    ic(f"Update interval: {update_interval} seconds")

    conn = sqlite3.connect(db_path)
    create_table(conn)

    while True:
        ic(f"Fetching news at {datetime.now()}")
        fetch_and_store_news(conn, sources)
        ic(f"Sleeping for {update_interval} seconds")
        time.sleep(update_interval)

if __name__ == "__main__":
    main()
