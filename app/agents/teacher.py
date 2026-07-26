from app.providers.factory import ProviderFactory


class TeacherAgent:

    def __init__(self):
        self.provider = ProviderFactory.create()

    def ask(self, prompt: str) -> str:
        return self.provider.generate(prompt)