import dspy

turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.settings.configure(lm=turbo)

def summarize_article(article):
    prompt = f"Summarize the following article: {article}"
    summary = turbo.complete(prompt).text
    return summary.strip()
