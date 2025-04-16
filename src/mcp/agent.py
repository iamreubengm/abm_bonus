import os
import requests
import time

class MCPAgent:    
    def __init__(self, name, description, model_name):
        self.name = name
        self.description = description
        self.model_name = model_name
        self.context = []
    
    def add_to_context(self, message):
        self.context.append(message)
    
    def generate_response(self, prompt):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        messages = []
        
        for msg in self.context:
            role = "assistant" if msg.role == self.name else "user"
            messages.append({"role": role, "content": msg.content})
        
        messages.append({"role": "user", "content": prompt})
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "anthropic-version": "2023-06-01",
                        "x-api-key": api_key,
                        "content-type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "system": self.description,
                        "messages": messages,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    return response.json()["content"][0]["text"]
                elif response.status_code == 529:
                    print(f"API overloaded. Retrying in {retry_delay} seconds (attempt {attempt+1}/{max_retries})...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise Exception(f"API call failed ({response.status_code}): {response.text}")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
        
        raise Exception("Maximum retries exceeded. API still overloaded.")