# News Aggregator

A compact news aggregator that fetches articles from various RSS sources, processes them, and stores them in a SQLite database.

## Features

- Fetches news from multiple configurable RSS feeds
- Detects language of news items
- Extracts topics from news items
- Stores news in SQLite with metadata (language, topics, etc.)
- Avoids duplicate entries
- Runs continuously with configurable update intervals
- Interactive setup for easy configuration

## Requirements

- Python 3.6+
- Dependencies: feedparser, langdetect, nltk, python-daemon, python-dotenv

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/news-aggregator.git
   cd news-aggregator
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download NLTK data:
   ```
   python download_nltk_data.py
   ```

## Configuration

1. Run the setup script:
   ```
   python setup.py
   ```
   This guides you through RSS feed setup and creates `config.json`.

2. (Optional) Manually edit `config.json`:
   - Adjust database path
   - Set update interval
   - Modify RSS sources

## Usage

1. Run the main script:
   ```
   python news_aggregator.py
   ```

   This will run the script in the foreground.

2. To run the script in the background (Unix-like systems only):
   ```
   python news_aggregator.py --background
   ```

   This will use the python-daemon library to run the script as a daemon process.

   Note: On Windows, the `--background` option is not supported. The script will always run in the foreground, but you can minimize the console window.

The script fetches news continuously based on the configured interval.

Note: When running in the background on Unix-like systems, logs will be written to 'news_aggregator.log' instead of being printed to the console. On Windows, logs are always printed to the console.

### Windows-specific Instructions

- When running on Windows, make sure to use backslashes (\) in file paths in your `config.json` file.
- The `python-daemon` library is not supported on Windows. The script will always run in the foreground.
- To run the script in the background on Windows, you can use the Task Scheduler or create a batch file to start the script and run it minimized.

## Development

- Use the `dev` branch for ongoing development
- Create feature branches from `dev`
- Submit pull requests to `dev`

## Testing

Run unit tests:
```
python -m unittest test_news_aggregator.py
```

## Future Enhancements

- Improve error handling for RSS parsing
- Add periodic database cleanup
- Create a web interface for viewing aggregated news
- Implement search functionality
- Add export options for news items
- Develop user preferences for news filtering
- Integrate with external APIs for additional data enrichment
- Implement multi-threading for faster processing of multiple feeds

## Contributing

Please follow the SEARCH/REPLACE block format for proposing changes. See the Contributing section in the full README for detailed guidelines.

## License

[MIT License](LICENSE)
