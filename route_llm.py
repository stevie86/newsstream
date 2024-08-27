class Router:
    def __init__(self):
        self.rules = []

    def add_rule(self, condition, model):
        self.rules.append((condition, model))

    def route(self, input_text):
        for condition, model in self.rules:
            if condition(input_text):
                return model.generate(input_text)
        raise ValueError("No matching rule found for input")

class OpenAILLM:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate(self, prompt):
        # Placeholder for actual OpenAI API call
        return f"Generated text using {self.model_name}: {prompt}"
