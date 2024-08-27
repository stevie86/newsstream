from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import nltk

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def extract_topics(text, num_topics=3):
    # Tokenize and preprocess the text
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    processed_text = ' '.join(tokens)

    # Create and fit TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=1000)
    tfidf_matrix = vectorizer.fit_transform([processed_text])

    # Get feature names (words)
    feature_names = vectorizer.get_feature_names_out()

    # Normalize the TF-IDF matrix
    normalized_tfidf = normalize(tfidf_matrix)

    # Get the top N topics
    top_n_indices = normalized_tfidf.toarray()[0].argsort()[-num_topics:][::-1]
    top_topics = [feature_names[i] for i in top_n_indices]

    return ','.join(top_topics) if top_topics else 'unknown'
