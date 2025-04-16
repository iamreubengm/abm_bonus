class MCPMessage:    
    def __init__(self, role, content, metadata = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata
        }
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"