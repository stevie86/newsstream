import json
import sqlite3
import feedparser
from datetime import datetime
import time
from langdetect import detect
from newspaper import Article
import nltk

nltk.download('punkt')

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

def extract_topic(text):
    article = Article('')
    article.set_text(text)
    article.parse()
    article.nlp()
    return article.keywords[0] if article.keywords else 'unknown'

def insert_news_item(conn, item, source):
    try:
        language = detect_language(item.title + ' ' + item.description)
        topic = extract_topic(item.title + ' ' + item.description)
        
        conn.execute('''INSERT INTO news_items (title, link, description, pub_date, source, language, topic)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (item.title, item.link, item.description,
                      item.published, source, language, topic))
        conn.commit()
    except sqlite3.IntegrityError:
        # Skip duplicate entries
        pass

def fetch_and_store_news(conn, sources):
    for source in sources:
        feed = feedparser.parse(source['url'])
        for entry in feed.entries:
            insert_news_item(conn, entry, source['name'])

def main():
    config = load_config('config.json')
    db_path = config['database_path']
    sources = config['sources']
    update_interval = config['update_interval']

    conn = sqlite3.connect(db_path)
    create_table(conn)

    while True:
        print(f"Fetching news at {datetime.now()}")
        fetch_and_store_news(conn, sources)
        time.sleep(update_interval)

if __name__ == "__main__":
    main()
