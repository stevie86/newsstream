from dotenv import load_dotenv
import os
from typing import List
import openai
from contextlib import contextmanager

from src.aggregator import fetch_rss_feed, scrape_website
from src.summarizer import summarize_article
from src.script_generator import ScriptGenerator
from src.validator import validate_script

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

def get_article_summaries(rss_feed_url: str) -> List[str]:
    """Fetch RSS feed and summarize articles."""
    try:
        rss_articles = fetch_rss_feed(rss_feed_url)
        return [summarize_article(article['description']) for _, article in rss_articles.iterrows()]
    except Exception as e:
        print(f"Error fetching or summarizing articles: {e}")
        return []

def main():
    """
    Main function to orchestrate the news processing and script generation.
    
    This function performs the following steps:
    1. Fetches and summarizes articles from an RSS feed
    2. Generates a YouTube script based on the article summaries
    3. Validates the generated script
    """
    rss_feed_url = "https://feeds.washingtonpost.com/rss/rss_fact-checker?itid=lk_inline_manual_4"
    
    with set_openai_api_key():
        # Fetch and summarize articles
        summaries = get_article_summaries(rss_feed_url)
        
        if not summaries:
            print("No summaries generated. Exiting.")
            return

        # Concatenate summaries into a single string
        concatenated_summaries = "\n\n".join(summaries)

        # Generate YouTube scripts
        script_generator = ScriptGenerator()
        try:
            script = script_generator(summaries=concatenated_summaries)
        except Exception as e:
            print(f"Error generating script: {e}")
            return

        # Validate script
        if validate_script(script):
            print("Script is valid.")
            print(script)
        else:
            print("Script validation failed.")

if __name__ == "__main__":
    main()
