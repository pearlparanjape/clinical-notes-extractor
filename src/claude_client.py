from dotenv import load_dotenv
import anthropic
from src import config

load_dotenv()


class ClaudeClient:
    """The real Claude. Same .complete() interface as FakeClient,
    but actually calls the Claude API instead of returning canned responses."""

    def __init__(self, model: str = config.MODEL):
        self.client = anthropic.Anthropic()
        self.model = model

    def complete(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
