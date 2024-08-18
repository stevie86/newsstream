import dspy

class GenerateScript(dspy.Signature):
    summaries = dspy.InputField()
    script = dspy.OutputField(desc="The generated YouTube script")

class ScriptGenerator(dspy.Module):
    def __init__(self):
        self.generate_script = dspy.ChainOfThought(GenerateScript)
       
    def forward(self, summaries):
        script = self.generate_script(summaries=summaries).script
        return script
