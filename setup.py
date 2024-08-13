import json
import re
import requests

def get_feed_info():
    url = input("Enter the URL of the RSS feed: ")
    custom_name = input("Do you want to assign a custom name? (y/n): ").lower().strip()
    if custom_name == 'y':
        name = input("Enter the custom name for this feed: ")
    else:
        name = url.split('//')[1].split('/')[0]  # Use domain as default name
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

    while True:
        feed = get_feed_info()
        if validate_url(feed["url"]):
            config["sources"].append(feed)
            print(f"Added {feed['name']} successfully!")
        else:
            print("Invalid URL. Please try again.")
        
        add_another = input("Do you want to add another RSS feed? (y/n): ").lower().strip()
        if add_another != 'y':
            break

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    print("Configuration saved to config.json")

if __name__ == "__main__":
    setup_config()
