from dotenv import load_dotenv
import os
import openai
from contextlib import contextmanager
import json
import time
import logging
from logging.handlers import RotatingFileHandler

from src.aggregator import fetch_rss_feed, process_news_item
from src.database import create_connection, create_table, check_and_update_db_structure, insert_or_update_news_item
from src.summarizer import summarize_article
from src.script_generator import ScriptGenerator
from src.validator import validate_script
from route_config import router

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('news_aggregator.log', maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

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

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def fetch_and_store_news(conn, sources):
    for source in sources:
        logger.info(f"Fetching news from: {source['name']}")
        feed = fetch_rss_feed(source['url'])
        logger.info(f"Found {len(feed)} entries")
        for _, item in feed.iterrows():
            processed_item = process_news_item(item, source['name'])
            insert_or_update_news_item(conn, processed_item)

def main():
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

    while True:
        logger.info(f"Fetching news at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        fetch_and_store_news(conn, sources)
        logger.info(f"Sleeping for {update_interval} seconds")
        time.sleep(update_interval)

if __name__ == "__main__":
    main()
