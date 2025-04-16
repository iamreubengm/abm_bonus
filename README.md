# abm_bonus
Repository for the bonus MCP assignment in 94815: Agent-based Modeling and Agentic Technology  
  
 A multi-agent debate system that orchestrates interactions between specialized AI agents using a custom Model Context Protocol (MCP) implementation. The system features three agents: a Pro debater, a Con debater, and a Moderator, who engage in structured debates on user-specified topics.  
  
## Installation Instruction
1. Clone this repository:
```
git clone https://github.com/iamreubengm/abm_bonus.git
cd abm_bonus
``` 
  
2. Install the required dependencies:
```
pip install -r requirements.txt
```  
  
3. Set up your API key - Create a .env file in the root directory:
```
ANTHROPIC_API_KEY=''
```  
  
## Running the Agents:  
To start the web interface, run the command below:    
```
python web_interface.py
```  
  
Then open your browser and navigate to: http://127.0.0.1:5000
Through the web interface, you can:  
- Enter a debate topic  
- Select the number of debate rounds  
- Start the debate and watch it progress in real-time  
- Download the debate transcript when completed  
  
  





