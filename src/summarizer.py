try:
    from route_config import router
except ImportError:
    print("Warning: route_config module not found. Using fallback summarization.")
    router = None

def summarize_article(article, router=None):
    if router:
        prompt = f"Summarize the following article: {article}"
        summary = router.route(prompt)
        return summary.strip()
    else:
        # Fallback summarization method
        words = article.split()
        return ' '.join(words[:30]) + "..."  # Simple truncation as a fallback
import sqlite3
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_top_articles(conn, limit=5):
    """Fetch the top articles from the last 24 hours."""
    cursor = conn.cursor()
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        SELECT title, description, source
        FROM news_items
        WHERE pub_date > ?
        ORDER BY pub_date DESC
        LIMIT ?
    """, (yesterday, limit))
    return cursor.fetchall()

def summarize_article(title, description, source):
    """Summarize a single article using OpenAI's API."""
    prompt = f"Summarize this news article in one short, exciting sentence for a YouTube Short script:\n\nTitle: {title}\nSource: {source}\nDescription: {description}"
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    return response.choices[0].text.strip()

def generate_youtube_short_script(conn):
    """Generate a script for a YouTube Short based on top news articles."""
    articles = get_top_articles(conn)
    script = "Hey there, news junkies! 👋 Let's dive into today's top stories:\n\n"
    
    for i, article in enumerate(articles, 1):
        title, description, source = article
        summary = summarize_article(title, description, source)
        script += f"{i}. 🔥 {summary}\n\n"
    
    script += "That's all for now! 🎬 Remember to like, subscribe, and hit that notification bell for your daily dose of news shorts! 🔔\n"
    script += "See you tomorrow for more breaking stories! 👋"
    return script
