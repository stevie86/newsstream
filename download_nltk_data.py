import nltk
import ssl
import sys

def download_nltk_data():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

if __name__ == "__main__":
    print("Downloading required NLTK data...")
    download_nltk_data()
    print("NLTK data download complete.")
