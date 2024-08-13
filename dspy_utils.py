import dspy
from dspy.retrieve.ollama_retrieve import OllamaRetrieve

def initialize_dspy(model_name="mistral:latest"):
    """
    Initialize DSPy with the specified model.
    """
    ollama = OllamaRetrieve(model=model_name)
    dspy.settings.configure(lm=ollama)

class TopicExtractor(dspy.Signature):
    """Extract the main topic from a given text."""

    text = dspy.InputField()
    topic = dspy.OutputField(desc="The main topic of the text")

class LanguageDetector(dspy.Signature):
    """Detect the language of a given text."""

    text = dspy.InputField()
    language = dspy.OutputField(desc="The detected language code (e.g., 'en' for English)")

def dspy_extract_topic(text):
    """
    Extract topic from text using DSPy.
    """
    topic_extractor = dspy.Predict(TopicExtractor)
    result = topic_extractor(text=text)
    return result.topic

def dspy_detect_language(text):
    """
    Detect language of text using DSPy.
    """
    language_detector = dspy.Predict(LanguageDetector)
    result = language_detector(text=text)
    return result.language

# Initialize DSPy with default model
initialize_dspy()

# Add more DSPy-related functions as needed
