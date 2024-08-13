# News Aggregator

This is a compact news aggregator that fetches news from various RSS sources, detects the language and topic of each article, and stores them in an SQLite database. The aggregator is configurable via a JSON file and includes an interactive setup script for easy configuration.

## Features

- Fetches news from multiple RSS feeds
- Detects language of news items
- Extracts topics from news items
- Stores news items in an SQLite database with language and topic information
- Configurable via JSON file
- Interactive setup script for easy configuration
- Avoids duplicate entries
- Runs continuously with a configurable update interval

## Requirements

- Python 3.6+
- Libraries: feedparser, langdetect, newspaper3k, nltk, requests

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/news-aggregator.git
   cd news-aggregator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Run the interactive setup script:
   ```
   python setup.py
   ```
   This will guide you through setting up your RSS feeds and create the `config.json` file.

2. (Optional) Manually edit the `config.json` file to adjust:
   - Database path
   - Update interval (in seconds)
   - RSS sources (name and URL)

## Usage

1. Run the setup script (if you haven't already):
   ```
   python setup.py
   ```

2. Run the main script:
   ```
   python news_aggregator.py
   ```

The script will continuously fetch news from the specified sources, detect the language and topic of each item, and store them in the SQLite database.

## Development

This project uses a dev branch for ongoing development. To contribute:

1. Create a new branch from dev:
   ```
   git checkout -b feature/your-feature-name dev
   ```

2. Make your changes and commit them
3. Push your branch and create a pull request to the dev branch

Major releases will be merged into the main branch periodically.

## Future Enhancements

- Implement error handling and retry mechanisms for RSS feed parsing
- Add a feature to periodically clean up old news items from the database
- Implement a simple web interface to view the aggregated news items
- Add support for categorizing news items into predefined categories
- Implement a search functionality to find news items by keywords
- Add support for exporting news items in various formats
- Implement user preferences for filtering news items based on topics or sources

## License

[MIT License](LICENSE)
