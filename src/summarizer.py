from route_config import router

def summarize_article(article, router):
    prompt = f"Summarize the following article: {article}"
    summary = router.route(prompt).text
    return summary.strip()
