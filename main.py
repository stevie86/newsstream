import json
import sqlite3
import feedparser
from datetime import datetime
import time
import logging
from logging.handlers import RotatingFileHandler
import argparse
import signal
import sys
import daemon
from dotenv import load_dotenv
import os
import openai
from contextlib import contextmanager

from src.aggregator import fetch_rss_feed, process_news_item, detect_language, extract_topic
from src.database import create_connection, create_table, check_and_update_db_structure, insert_or_update_news_item
from src.summarizer import summarize_article
from src.script_generator import ScriptGenerator
from src.validator import validate_script
from route_config import router

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

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@contextmanager
def set_openai_api_key():
    """Context manager to set and reset the OpenAI API key."""
    original_api_key = openai.api_key
    openai.api_key = OPENAI_API_KEY
    try:
        yield
    finally:
        openai.api_key = original_api_key

def fetch_and_store_news(conn, sources):
    for source in sources:
        logger.info(f"Fetching news from: {source['name']}")
        feed = feedparser.parse(source['url'])
        logger.info(f"Found {len(feed.entries)} entries")
        for entry in feed.entries:
            processed_item = process_news_item(entry, source['name'])
            insert_or_update_news_item(conn, processed_item)

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

    conn = create_connection(db_path)
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
