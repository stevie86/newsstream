import json
import requests
from typing import List, Dict, Optional
import os

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

def get_multiple_feeds(existing_feeds: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Get multiple RSS feeds from user input and retain existing feeds if desired."""
    feeds = []
    
    # Ask about existing feeds
    for feed in existing_feeds:
        keep = input(f"Do you want to keep the existing feed '{feed['name']}' ({feed['url']})? (y/n): ").lower().strip()
        if keep == 'y':
            feeds.append(feed)
            print(f"Kept existing feed: {feed['name']}")
        else:
            print(f"Removed feed: {feed['name']}")
    
    print("\nLet's add new RSS feeds to your configuration.")
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

def load_existing_config() -> Dict[str, Any]:
    """Load existing configuration if available."""
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error reading existing config. Starting with default values.")
    return {}

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to config.json with {len(config['sources'])} RSS feeds.")
    except IOError as e:
        print(f"Error saving configuration: {e}")

def setup_config() -> None:
    """Set up the configuration file with user input."""
    existing_config = load_existing_config()
    
    existing_feeds = existing_config.get('sources', [])
    
    config = {
        "database_path": existing_config.get('database_path', "news.db"),
        "update_interval": existing_config.get('update_interval', 3600),
        "sources": get_multiple_feeds(existing_feeds)
    }

    save_config(config)

def main() -> None:
    try:
        setup_config()
    except KeyboardInterrupt:
        print("\nSetup interrupted. Configuration not saved.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    else:
        print("Setup completed successfully.")

if __name__ == "__main__":
    main()
