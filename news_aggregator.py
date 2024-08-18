import json
import sqlite3
import feedparser
from datetime import datetime
import time
from langdetect import detect
import nltk
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
from dspy_utils import dspy_extract_topic, dspy_detect_language
import argparse
import signal
import sys
import daemon

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Database version
DB_VERSION = 2

# Global variable to control the main loop
running = True

def setup_logging(is_daemon=False):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if is_daemon:
        file_handler = RotatingFileHandler('news_aggregator.log', maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    global running
    logger.info("Received shutdown signal. Gracefully shutting down...")
    running = False

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
                     topics TEXT,
                     last_updated TEXT)''')
    
    # Add the last_updated column if it doesn't exist
    try:
        conn.execute("ALTER TABLE news_items ADD COLUMN last_updated TEXT")
        logger.info("Added 'last_updated' column to news_items table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.info("'last_updated' column already exists")
        else:
            logger.error(f"Error adding 'last_updated' column: {e}")
    
    # Create a table to store the database version
    conn.execute('''CREATE TABLE IF NOT EXISTS db_version
                    (version INTEGER)''')
    
    # Check if version exists, if not, insert it
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM db_version")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO db_version (version) VALUES (?)", (DB_VERSION,))
    conn.commit()

def backup_database(db_path):
    backup_path = f"{db_path}.bak"
    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backed up to {backup_path}")

def check_and_update_db_structure(conn, db_path):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT version FROM db_version")
        current_version = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        logger.warning("db_version table not found. Assuming version 1.")
        current_version = 1
        conn.execute('''CREATE TABLE IF NOT EXISTS db_version
                        (version INTEGER)''')
        conn.execute("INSERT INTO db_version (version) VALUES (?)", (current_version,))
        conn.commit()
    
    if current_version < DB_VERSION:
        logger.info(f"Updating database from version {current_version} to {DB_VERSION}")
        backup_database(db_path)
        
        # Perform necessary updates based on version differences
        if current_version == 1:
            # Add the 'topics' column if it doesn't exist
            try:
                conn.execute("ALTER TABLE news_items ADD COLUMN topics TEXT")
                logger.info("Added 'topics' column to news_items table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("'topics' column already exists")
                else:
                    logger.error(f"Error adding 'topics' column: {e}")
            
            # Add the 'last_updated' column if it doesn't exist
            try:
                conn.execute("ALTER TABLE news_items ADD COLUMN last_updated TEXT")
                logger.info("Added 'last_updated' column to news_items table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("'last_updated' column already exists")
                else:
                    logger.error(f"Error adding 'last_updated' column: {e}")
        
        # Update the version in the database
        conn.execute("UPDATE db_version SET version = ?", (DB_VERSION,))
        conn.commit()
        logger.info("Database structure updated successfully")

def detect_language(text):
    try:
        return dspy_detect_language(text)
    except:
        # Fallback to the original method if DSPy fails
        try:
            return detect(text)
        except:
            return 'unknown'

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

def extract_topic(text):
    try:
        return dspy_extract_topic(text)
    except:
        # Fallback to the original method if DSPy fails
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
        word_freq = Counter(tokens)
        return word_freq.most_common(1)[0][0] if word_freq else 'unknown'

def insert_or_update_news_item(conn, item, source):
    try:
        description = getattr(item, 'description', '')
        language = detect_language(item.title + ' ' + description)
        topics = [extract_topic(item.title + ' ' + description)]
        
        logger.debug(f"Processing item: {item.title}, Source: {source}, Language: {language}, Topics: {topics}")
        
        pub_date = getattr(item, 'published', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM news_items WHERE link = ?", (item.link,))
        existing_item = cursor.fetchone()
        
        if existing_item:
            conn.execute('''UPDATE news_items 
                            SET title = ?, description = ?, pub_date = ?, 
                                source = ?, language = ?, topics = ?, last_updated = ?
                            WHERE link = ?''',
                         (item.title, description, pub_date, source, 
                          language, ','.join(topics), current_time, item.link))
            logger.info(f"Updated existing item: {item.title}")
        else:
            conn.execute('''INSERT INTO news_items 
                            (title, link, description, pub_date, source, language, topics, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (item.title, item.link, description, pub_date, 
                          source, language, ','.join(topics), current_time))
            logger.info(f"Inserted new item: {item.title}")
        
        conn.commit()
    except AttributeError as e:
        logger.error(f"Error processing item: {e}")
        logger.error(f"Item attributes: {vars(item)}")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

def fetch_and_store_news(conn, sources):
    for source in sources:
        logger.info(f"Fetching news from: {source['name']}")
        feed = feedparser.parse(source['url'])
        logger.info(f"Found {len(feed.entries)} entries")
        for entry in feed.entries:
            insert_or_update_news_item(conn, entry, source['name'])

def main(is_daemon=False):
    global logger
    logger = setup_logging(is_daemon)

    config = load_config('config.json')
    db_path = config['database_path']
    sources = config['sources']
    update_interval = config['update_interval']
    logger.info(f"Database path: {db_path}")
    logger.info(f"Number of sources: {len(sources)}")
    logger.info(f"Update interval: {update_interval} seconds")

    conn = sqlite3.connect(db_path)
    create_table(conn)
    check_and_update_db_structure(conn, db_path)

    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while running:
        logger.info(f"Fetching news at {datetime.now()}")
        fetch_and_store_news(conn, sources)
        logger.info(f"Sleeping for {update_interval} seconds")
        time.sleep(update_interval)

    logger.info("Shutting down gracefully...")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="News Aggregator")
    parser.add_argument("--daemon", action="store_true", help="Run as a daemon process")
    args = parser.parse_args()

    if args.daemon:
        with daemon.DaemonContext():
            main(is_daemon=True)
    else:
        main(is_daemon=False)
