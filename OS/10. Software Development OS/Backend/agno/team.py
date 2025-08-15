class Team:
    def __init__(self, members=None, model=None, mode=None, success_criteria=None, instructions=None, expected_output=None):
        self.members = members or []
        self.model = model
        self.mode = mode
        self.success_criteria = success_criteria
        self.instructions = instructions
        self.expected_output = expected_output
    
    def run(self, text):
        return MockResponse(f"Mock team response from team with {len(self.members)} members: {text}")
    
    def chat(self, text):
        return MockResponse(f"Mock team chat from team with {len(self.members)} members: {text}")

class MockResponse:
    def __init__(self, content):
        self.content = content
