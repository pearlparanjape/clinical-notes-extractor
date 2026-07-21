class FakeClient:
    """Stand-in for Claude. Same .complete() interface as ClaudeClient,
    but returns a canned response instead of calling the API."""

    def __init__(self, canned_response: str):
        self.canned_response = canned_response

    def complete(self, prompt: str) -> str:
        return self.canned_response
