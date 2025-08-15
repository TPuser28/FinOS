class MistralChat:
    def __init__(self, api_key=None, id=None):
        self.api_key = api_key
        self.id = id
    
    def chat(self, messages):
        return MockResponse("Mock Mistral response")
    
    def complete(self, prompt):
        return MockResponse("Mock Mistral completion")

class MockResponse:
    def __init__(self, content):
        self.content = content
