import json
import sqlite3
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
import platform
from contextlib import contextmanager

from src.aggregator import fetch_rss_feed, process_news_item
from src.database import create_connection, create_table, check_and_update_db_structure, insert_or_update_news_item
from src.summarizer import generate_youtube_short_script
from src.summarizer import summarize_article
from src.script_generator import ScriptGenerator
from src.validator import validate_script

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
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error(f"Config file not found: {file_path}")
        sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables")
    sys.exit(1)

def fetch_and_store_news(conn, sources):
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

    try:
        conn = create_connection(db_path)
        create_table(conn)
        check_and_update_db_structure(conn, db_path)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)

    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while running:
        logger.info(f"Fetching news at {datetime.now()}")
        fetch_and_store_news(conn, sources)
        
        # Generate and save YouTube Short script
        script = generate_youtube_short_script(conn)
        script_filename = f"youtube_short_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(script_filename, 'w') as f:
            f.write(script)
        logger.info(f"YouTube Short script saved to {script_filename}")
        
        logger.info(f"Sleeping for {update_interval} seconds")
        time.sleep(update_interval)

    logger.info("Shutting down gracefully...")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="News Aggregator")
    parser.add_argument("--background", action="store_true", help="Run in background mode")
    args = parser.parse_args()

    if args.background and platform.system() != "Windows":
        try:
            import daemon
            with daemon.DaemonContext():
                main(is_daemon=True)
        except ImportError:
            print("Daemon module not available. Running in foreground.")
            main(is_daemon=False)
    else:
        main(is_daemon=False)
