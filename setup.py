import json
import re
import requests

def get_feed_info():
    name = input("Enter the name of the RSS feed: ")
    url = input("Enter the URL of the RSS feed: ")
    return {"name": name, "url": url}

def validate_url(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

def setup_config():
    config = {
        "database_path": "news.db",
        "update_interval": 3600,
        "sources": []
    }

    num_feeds = int(input("How many RSS feeds would you like to add? "))
    
    for _ in range(num_feeds):
        while True:
            feed = get_feed_info()
            if validate_url(feed["url"]):
                config["sources"].append(feed)
                print(f"Added {feed['name']} successfully!")
                break
            else:
                print("Invalid URL. Please try again.")

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    print("Configuration saved to config.json")

if __name__ == "__main__":
    setup_config()
