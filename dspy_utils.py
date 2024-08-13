import dspy
from dspy.backends.ollama import OllamaBackend

# Initialize DSPy with Ollama backend using the Mistral model
ollama = OllamaBackend(model="mistral:latest")
dspy.configure(lm=ollama)

class TopicExtractor(dspy.Signature):
    """Extract the main topic from a given text."""

    text = dspy.InputField()
    topic = dspy.OutputField(desc="The main topic of the text")

class LanguageDetector(dspy.Signature):
    """Detect the language of a given text."""

    text = dspy.InputField()
    language = dspy.OutputField(desc="The detected language code (e.g., 'en' for English)")

topic_extractor = dspy.Predict(TopicExtractor)
language_detector = dspy.Predict(LanguageDetector)

def dspy_extract_topic(text):
    """
    Extract topic from text using DSPy.
    """
    result = topic_extractor(text=text)
    return result.topic

def dspy_detect_language(text):
    """
    Detect language of text using DSPy.
    """
    result = language_detector(text=text)
    return result.language

# Add more DSPy-related functions as needed
