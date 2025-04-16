from .message import MCPMessage

class MCPOrchestrator:    
    def __init__(self):
        self.agents = {}
        self.conversation_history = []
    
    def register_agent(self, agent):
        self.agents[agent.name] = agent
        print(f"Agent '{agent.name}' registered successfully")
    
    def send_message(self, from_agent, to_agent, content, metadata = None):
        sender = self.agents.get(from_agent) if from_agent != "Human" else None
        receiver = self.agents.get(to_agent)
        
        if from_agent != "Human" and not sender:
            raise ValueError(f"Agent not found: {from_agent}")
        
        if not receiver:
            raise ValueError(f"Receiving agent not found: {to_agent}")
        
        message = MCPMessage(role=from_agent, content=content, metadata=metadata)
        self.conversation_history.append(message)
        receiver.add_to_context(message)
        
        print(f"Message sent: {from_agent} → {to_agent} [{len(content)} chars]")
        return message