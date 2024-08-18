from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now you can access the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

from src.aggregator import fetch_rss_feed, scrape_website
from src.summarizer import summarize_article
from src.script_generator import ScriptGenerator
from src.validator import validate_script

def main():
    # Set the OpenAI API key for DSPy
    import openai
    openai.api_key = openai_api_key

    # Fetch and scrape articles
    rss_feed_url = "https://feeds.washingtonpost.com/rss/rss_fact-checker?itid=lk_inline_manual_4"
    rss_articles = fetch_rss_feed(rss_feed_url)
    
    website_url = "https://example.com/news"
    articles = scrape_website(website_url, ".article", ".title", ".content")

    # Summarize articles
    summaries = [summarize_article(article['description']) for _, article in rss_articles.iterrows()]

    # Concatenate summaries into a single string
    concatenated_summaries = "\n\n".join(summaries)

    # Generate YouTube scripts
    script_generator = ScriptGenerator()
    script = script_generator(summaries=concatenated_summaries)

    # Validate script
    if validate_script(script):
        print("Script is valid.")
        print(script)
    else:
        print("Script validation failed.")

if __name__ == "__main__":
    main()
