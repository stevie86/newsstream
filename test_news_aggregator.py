import unittest
import json
import sqlite3
import logging
from news_aggregator import (
    load_config,
    create_table,
    detect_language,
    extract_topic,
    insert_or_update_news_item,
    DB_VERSION,
)
from unittest.mock import patch, MagicMock

# Set up a null logger for testing
logging.getLogger('news_aggregator').addHandler(logging.NullHandler())

class TestNewsAggregator(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        create_table(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_load_config(self):
        config = load_config('config.json')
        self.assertIsInstance(config, dict)
        self.assertIn('database_path', config)
        self.assertIn('update_interval', config)
        self.assertIn('sources', config)

    def test_detect_language(self):
        self.assertEqual(detect_language('Hello, world!'), 'en')
        self.assertEqual(detect_language('Bonjour le monde!'), 'fr')
        self.assertEqual(detect_language('Hola mundo!'), 'es')

    def test_extract_topic(self):
        text = "The quick brown fox jumps over the lazy dog"
        topic = extract_topic(text)
        self.assertIn(topic, ['quick', 'brown', 'fox', 'jumps', 'lazy', 'dog'])

    @patch('news_aggregator.detect_language')
    @patch('news_aggregator.extract_topic')
    def test_insert_or_update_news_item(self, mock_extract_topic, mock_detect_language):
        mock_detect_language.return_value = 'en'
        mock_extract_topic.return_value = 'test'

        item = MagicMock()
        item.title = "Test Title"
        item.link = "http://example.com/test"
        item.description = "Test Description"
        item.published = "2023-05-01 12:00:00"

        insert_or_update_news_item(self.conn, item, "Test Source")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM news_items WHERE link = ?", (item.link,))
        result = cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[1], "Test Title")
        self.assertEqual(result[2], "http://example.com/test")
        self.assertEqual(result[3], "Test Description")
        self.assertEqual(result[4], "2023-05-01 12:00:00")
        self.assertEqual(result[5], "Test Source")
        self.assertEqual(result[6], "en")
        self.assertEqual(result[7], "test")

if __name__ == '__main__':
    unittest.main()
