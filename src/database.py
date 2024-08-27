import sqlite3
import logging
import shutil

logger = logging.getLogger(__name__)

DB_VERSION = 2

import sqlite3
import shutil
import logging
from datetime import datetime

logger = logging.getLogger('news_aggregator')

DB_VERSION = 2

def create_connection(db_path):
    return sqlite3.connect(db_path)

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
    
    conn.execute('''CREATE TABLE IF NOT EXISTS db_version
                    (version INTEGER)''')
    
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
        
        if current_version == 1:
            try:
                conn.execute("ALTER TABLE news_items ADD COLUMN topics TEXT")
                logger.info("Added 'topics' column to news_items table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    logger.error(f"Error adding 'topics' column: {e}")
            
            try:
                conn.execute("ALTER TABLE news_items ADD COLUMN last_updated TEXT")
                logger.info("Added 'last_updated' column to news_items table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    logger.error(f"Error adding 'last_updated' column: {e}")
        
        conn.execute("UPDATE db_version SET version = ?", (DB_VERSION,))
        conn.commit()
        logger.info("Database structure updated successfully")

def insert_or_update_news_item(conn, item):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM news_items WHERE link = ?", (item['link'],))
        existing_item = cursor.fetchone()
        
        if existing_item:
            conn.execute('''UPDATE news_items 
                            SET title = ?, description = ?, pub_date = ?, 
                                source = ?, language = ?, topics = ?, last_updated = ?
                            WHERE link = ?''',
                         (item['title'], item['description'], item['pub_date'], item['source'], 
                          item['language'], item['topics'], item['last_updated'], item['link']))
            logger.info(f"Updated existing item: {item['title']}")
        else:
            conn.execute('''INSERT INTO news_items 
                            (title, link, description, pub_date, source, language, topics, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (item['title'], item['link'], item['description'], item['pub_date'], 
                          item['source'], item['language'], item['topics'], item['last_updated']))
            logger.info(f"Inserted new item: {item['title']}")
        
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        logger.error(f"Error inserting/updating news item: {e}")
        conn.rollback()

def detect_language_for_existing_entries(conn, detect_language_func):
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description FROM news_items WHERE language IS NULL OR language = 'unknown'")
    items = cursor.fetchall()
    
    for item in items:
        item_id, title, description = item
        text = f"{title} {description}"
        language = detect_language_func(text)
        
        conn.execute("UPDATE news_items SET language = ? WHERE id = ?", (language, item_id))
        logger.info(f"Updated language for item {item_id}: {language}")
    
    conn.commit()
    logger.info(f"Language detection completed for {len(items)} items")
