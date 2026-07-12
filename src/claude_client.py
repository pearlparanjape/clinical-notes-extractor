from dotenv import load_dotenv
import anthropic

load_dotenv()


class ClaudeClient:
    """The real Claude. Same .complete() interface as FakeClient,
    so it drops into extract_demographics with no other changes."""

    def __init__(self, model: str = "claude-haiku-4-5"):
        self.client = anthropic.Anthropic()
        self.model = model

    def complete(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
