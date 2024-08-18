import json
import requests
from typing import List, Dict

def get_feed_info() -> Dict[str, str]:
    """Get RSS feed information from user input."""
    url = input("Enter the URL of the RSS feed: ").strip()
    custom_name = input("Enter a custom name for this feed (press Enter to use default): ").strip()
    name = custom_name if custom_name else url.split('//')[1].split('/')[0]
    return {"name": name, "url": url}

def validate_url(url: str) -> bool:
    """Validate if the given URL is accessible."""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_multiple_feeds() -> List[Dict[str, str]]:
    """Get multiple RSS feeds from user input."""
    feeds = []
    print("Let's add RSS feeds to your configuration.")
    print("You can add multiple feeds. Enter 'done' when finished.")
    
    while True:
        feed = get_feed_info()
        if validate_url(feed["url"]):
            feeds.append(feed)
            print(f"Added {feed['name']} successfully!")
        else:
            print("Invalid or inaccessible URL. Please try again.")
        
        if input("Enter 'done' to finish, or press Enter to add another feed: ").lower().strip() == 'done':
            break
    
    return feeds

def setup_config():
    """Set up the configuration file with user input."""
    config = {
        "database_path": "news.db",
        "update_interval": 3600,
        "sources": get_multiple_feeds()
    }

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    print(f"Configuration saved to config.json with {len(config['sources'])} RSS feeds.")

if __name__ == "__main__":
    try:
        setup_config()
    except KeyboardInterrupt:
        print("\nSetup interrupted. Configuration not saved.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    else:
        print("Setup completed successfully.")
