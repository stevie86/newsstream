from route_config import router

class ScriptGenerator:
    def __init__(self, router):
        self.router = router

    def __call__(self, summaries):
        prompt = f"Generate a YouTube script based on the following summaries:\n\n{summaries}"
        script = self.router.route(prompt).text
        return script
