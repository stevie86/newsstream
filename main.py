import json
import sqlite3
from datetime import datetime
import time
import logging
import argparse
import signal
import sys
from dotenv import load_dotenv
import os
import platform

from src.aggregator import fetch_and_store_news
from src.database import create_connection, create_table, check_and_update_db_structure
from src.summarizer import generate_youtube_short_script
from src.logger import setup_logging

# Global variable to control the main loop
running = True

# Ensure the logger is set up at the module level
logger = setup_logging()

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

def main(is_daemon=False):
    global logger
    # Update the existing logger for daemon mode if necessary
    if is_daemon:
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                logger.removeHandler(handler)

    logger.info("Starting News Aggregator")
    logger.info(f"Daemon mode: {is_daemon}")

    try:
        config = load_config('config.json')
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return
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

    try:
        while running:
            logger.info(f"Fetching news at {datetime.now()}")
            fetch_and_store_news(conn, sources, logger)
            
            # Generate and save YouTube Short script
            script = generate_youtube_short_script(conn)
            if script:
                script_filename = f"youtube_short_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(script_filename, 'w') as f:
                    f.write(script)
                logger.info(f"YouTube Short script saved to {script_filename}")
            else:
                logger.warning("No script was generated.")
            
            logger.info(f"Sleeping for {update_interval} seconds")
            time.sleep(update_interval)
    except Exception as e:
        logger.error(f"An error occurred in the main loop: {e}")
    finally:
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
