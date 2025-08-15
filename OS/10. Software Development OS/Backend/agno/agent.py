class Agent:
    def __init__(self, model=None, name=None, description=None, instructions=None, tools=None, knowledge=None):
        self.model = model
        self.name = name
        self.description = description
        self.instructions = instructions
        self.tools = tools or []
        self.knowledge = knowledge or []
    
    def run(self, text):
        return MockResponse(f"Mock response from {self.name}: {text}")
    
    def chat(self, text):
        return MockResponse(f"Mock chat from {self.name}: {text}")

class MockResponse:
    def __init__(self, content):
        self.content = content
