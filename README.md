# News Aggregator

This is a compact news aggregator that fetches news from various RSS sources, detects the language and topic of each article, and stores them in an SQLite database. The aggregator is configurable via a JSON file and includes an interactive setup script for easy configuration.

## Features

- Fetches news from multiple RSS feeds
- Detects language of news items (using DSPy placeholder)
- Extracts topics from news items (using DSPy placeholder)
- Stores news items in an SQLite database with language and topic information
- Configurable via JSON file
- Interactive setup script for easy configuration
- Avoids duplicate entries
- Runs continuously with a configurable update interval

Note: The current implementation uses placeholder functions for DSPy-based language detection and topic extraction. These placeholders will be replaced with actual DSPy functionality in future updates.

## Requirements

- Python 3.6+
- Libraries: feedparser, langdetect, newspaper3k, nltk, requests, lxml[html_clean], dspy-ai

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
   Note: This will install all necessary dependencies, including lxml with HTML cleaning support and DSPy.

3. Download required NLTK data:
   ```
   python download_nltk_data.py
   ```
   This step is crucial for the language detection and topic extraction features to work correctly. The script will download the necessary NLTK data for both Windows and Linux systems.

4. Set up DSPy:
   - You'll need to configure DSPy with an API key or other necessary configurations. Refer to the DSPy documentation for specific setup instructions.

## LLM Setup for DSPy

DSPy supports various Language Models (LLMs). Here are some suggestions for setting up local LLMs using Ollama on both Windows and Linux:

### Ollama Setup

1. Install Ollama:
   - For Windows: Download and install from [Ollama's official website](https://ollama.ai/download)
   - For Linux: Run the following command:
     ```
     curl https://ollama.ai/install.sh | sh
     ```

2. Pull a model (e.g., llama2):
   ```
   ollama pull llama2
   ```

3. In your `dspy_utils.py` file, configure DSPy to use Ollama:
   ```python
   import dspy
   from dspy.backends.ollama import OllamaBackend

   ollama = OllamaBackend(model="llama2")
   dspy.configure(lm=ollama)
   ```

### Suggested Local LLMs

1. llama2: A powerful and versatile model suitable for various NLP tasks.
2. mistral: Known for its efficiency and performance.
3. vicuna: A fine-tuned version of LLaMA, optimized for dialogue and general text generation.
4. orca-mini: A smaller model suitable for systems with limited resources.

To use these models, simply replace "llama2" in the Ollama pull command and DSPy configuration with the desired model name.

## Configuration

1. Run the interactive setup script:
   ```
   python setup.py
   ```
   This will guide you through setting up your RSS feeds and create the `config.json` file.

2. (Optional) Manually edit the `config.json` file (create it if it doesn't exist) based on the `example-config.json` file to adjust:
   - Database path
   - Update interval (in seconds)
   - RSS sources (name and URL)
   - DSPy model (if using DSPy)

3. Configure the `route_config.py` file:
   The `route_config.py` file contains the configuration for the AI model routing. It defines which models or APIs are used for different tasks in the application. You may need to adjust this file based on your specific AI setup and requirements.

   Example structure of `route_config.py`:
   ```python
   from dspy.retrieve.bing_search import BingSearchRetriever
   from dspy.retrieve.pinecone import PineconeRetriever
   import dspy

   router = dspy.RetrieveAndRoute(
       retriever=BingSearchRetriever(),
       routes={
           'summarize': dspy.ChainOfThought('gpt-3.5-turbo'),
           'generate_script': dspy.ChainOfThought('gpt-4'),
           'validate_script': PineconeRetriever()
       }
   )
   ```
   Adjust the models, APIs, and routes according to your needs and available resources.

## Usage

1. Run the setup script (if you haven't already):
   ```
   python setup.py
   ```

2. Run the main script:
   ```
   python news_aggregator.py
   ```

The script will continuously fetch news from the specified sources, detect the language and topic of each item, generate tags and summaries using DSPy, and store them in the SQLite database.

## Testing

To run the unit tests for the news aggregator:

```
python -m unittest test_news_aggregator.py
```

This will run all the tests defined in the `test_news_aggregator.py` file, which include tests for config loading, language detection, topic extraction, and news item insertion/updating.

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
- Explore advanced DSPy features for improved topic extraction and summarization

## Contributing

When contributing to this project, please use the following format for proposing changes:

### SEARCH/REPLACE Block Rules

Every SEARCH/REPLACE block must use this format:
1. The file path alone on a line, verbatim.
2. The opening fence and code language, e.g., <source>python
3. The start of search block: <<<<<<< SEARCH
4. A contiguous chunk of lines to search for in the existing source code
5. The dividing line: =======
6. The lines to replace into the source code
7. The end of the replace block: >>>>>>> REPLACE
8. The closing fence: </source>

Guidelines:
- Every SEARCH section must EXACTLY MATCH the existing source code, character for character.
- SEARCH/REPLACE blocks will replace all matching occurrences.
- Keep SEARCH/REPLACE blocks concise.
- Break large changes into a series of smaller blocks.
- Only create SEARCH/REPLACE blocks for files that have been added to the discussion.
- To move code within a file, use 2 SEARCH/REPLACE blocks: one to delete from the current location, one to insert in the new location.
- For new files, use a SEARCH/REPLACE block with an empty SEARCH section.

Always return code changes in a SEARCH/REPLACE block format.

## License

[MIT License](LICENSE)
