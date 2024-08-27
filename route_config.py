try:
    from route_llm import Router, OpenAILLM

    router = Router()

    # Define your models
    gpt_3_5_turbo = OpenAILLM("gpt-3.5-turbo")
    gpt_4 = OpenAILLM("gpt-4")

    # Define routing rules
    router.add_rule(lambda x: len(x) > 1000, gpt_4)
    router.add_rule(lambda x: "complex" in x.lower(), gpt_4)
    router.add_rule(lambda x: True, gpt_3_5_turbo)  # Default rule

    # You can add more rules based on your specific needs
except ImportError:
    print("Warning: route_llm module not found. Using fallback summarization.")
    router = None
