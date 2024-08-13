# News Aggregator

This is a compact news aggregator that fetches news from various RSS sources and stores them in an SQLite database. The aggregator is configurable via a JSON file, allowing easy addition or removal of news sources.

## Features

- Fetches news from multiple RSS feeds
- Stores news items in an SQLite database
- Configurable via JSON file
- Avoids duplicate entries
- Runs continuously with a configurable update interval

## Requirements

- Python 3.6+
- feedparser library

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

Edit the `config.json` file to set your desired:
- Database path
- Update interval (in seconds)
- RSS sources (name and URL)

## Usage

Run the script:
```
python news_aggregator.py
```

The script will continuously fetch news from the specified sources and store them in the SQLite database.

## Development

This project uses a dev branch for ongoing development. To contribute:

1. Create a new branch from dev:
   ```
   git checkout -b feature/your-feature-name dev
   ```

2. Make your changes and commit them
3. Push your branch and create a pull request to the dev branch

Major releases will be merged into the main branch periodically.

## License

[MIT License](LICENSE)
