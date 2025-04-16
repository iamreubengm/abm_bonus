from flask import Flask, render_template, request, jsonify, send_file
import json
import threading
import time
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.orchestrator import MCPOrchestrator
from src.scenarios.debate import setup_debate_agents, debate_scenario

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = os.urandom(24)

active_debates = {}

@app.route('/')
def index():
    return render_template('index.html', 
                         default_topic="Artificial General Intelligence poses an existential risk to humanity", 
                         default_rounds=2)

@app.route('/start_debate', methods=['POST'])
def start_debate():
    data = request.json
    debate_id = str(int(time.time()))
    
    active_debates[debate_id] = {
        'topic': data.get('topic', "Artificial General Intelligence poses an existential risk to humanity"),
        'rounds': int(data.get('rounds', 2)),
        'status': 'initializing',
        'messages': [],
        'thread': None,
        'orchestrator': None
    }
    
    thread = threading.Thread(target=run_debate, args=(debate_id,))
    thread.daemon = True
    thread.start()
    active_debates[debate_id]['thread'] = thread
    
    return jsonify({'debate_id': debate_id, 'status': 'started'})

@app.route('/debate_status/<debate_id>', methods=['GET'])
def debate_status(debate_id):
    if debate_id not in active_debates:
        return jsonify({'error': 'Debate not found'}), 404
    
    debate = active_debates[debate_id]
    
    formatted_messages = []
    if debate['orchestrator'] and debate['orchestrator'].conversation_history:
        for msg in debate['orchestrator'].conversation_history:
            formatted_messages.append({
                'role': msg.role,
                'content': msg.content,
                'metadata': msg.metadata
            })
    else:
        formatted_messages = debate['messages']
    
    return jsonify({
        'status': debate['status'],
        'topic': debate['topic'],
        'rounds': debate['rounds'],
        'messages': formatted_messages
    })

@app.route('/download/<debate_id>', methods=['GET'])
def download_transcript(debate_id):
    if debate_id not in active_debates:
        return jsonify({'error': 'Debate not found'}), 404
    
    debate = active_debates[debate_id]
    
    filename = f'debate_{debate_id}.json'
    if not os.path.exists(filename) and debate['orchestrator']:
        with open(filename, 'w') as f:
            json.dump([msg.to_dict() for msg in debate['orchestrator'].conversation_history], f, indent=2)
    
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({'error': 'Transcript file not found'}), 404

def add_log_message(debate_id, message):
    if debate_id in active_debates:
        active_debates[debate_id]['messages'].append({
            'role': 'system',
            'content': message,
            'metadata': {'type': 'log'}
        })

def run_debate(debate_id):
    debate = active_debates[debate_id]
    
    try:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            debate['status'] = 'error'
            add_log_message(debate_id, "Error: ANTHROPIC_API_KEY environment variable is not set.")
            return
        
        add_log_message(debate_id, "Initializing debate system...")
        orchestrator = MCPOrchestrator()
        debate['orchestrator'] = orchestrator
        
        add_log_message(debate_id, "Setting up debate agents...")
        setup_debate_agents(orchestrator)
        
        debate['status'] = 'running'
        add_log_message(debate_id, f"Starting debate on topic: '{debate['topic']}'")
        
        conversation_history = debate_scenario(
            orchestrator, 
            debate['topic'], 
            debate['rounds']
        )
        
        filename = f'debate_{debate_id}.json'
        with open(filename, 'w') as f:
            json.dump([msg.to_dict() for msg in conversation_history], f, indent=2)
        
        debate['status'] = 'completed'
        add_log_message(debate_id, "Debate completed! You can download the transcript.")
        
    except Exception as e:
        debate['status'] = 'error'
        add_log_message(debate_id, f"Error in debate: {str(e)}")
        print(f"Error in debate: {e}")

if __name__ == '__main__':
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'index.html')
    if not os.path.exists(template_path):
        print(f"Creating template file at {template_path}")
        with open(template_path, 'w') as f:
            f.write("""<!DOCTYPE html>
            <html>
            <head>
                <title>MCP Debate Agents</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .debate-config { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                    .debate-log { background: #f9f9f9; padding: 20px; border-radius: 8px; height: 500px; overflow-y: auto; margin-bottom: 20px; }
                    .pro { color: #2c6b9e; border-left: 4px solid #2c6b9e; padding-left: 10px; margin: 10px 0; }
                    .con { color: #993333; border-left: 4px solid #993333; padding-left: 10px; margin: 10px 0; }
                    .moderator { color: #336633; border-left: 4px solid #336633; padding-left: 10px; margin: 10px 0; }
                    .system { color: #666; font-style: italic; margin: 5px 0; }
                    button { padding: 10px 15px; background: #4a86e8; color: white; border: none; border-radius: 4px; cursor: pointer; }
                    input, select { padding: 8px; margin: 5px 0 15px 0; width: 100%; box-sizing: border-box; }
                    h1, h2 { color: #333; }
                    hr { border: 0; height: 1px; background: #ddd; margin: 15px 0; }
                    .status-bar { background: #e5e5e5; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <h1>MCP Debate Agents</h1>
                
                <div class="debate-config">
                    <h2>Configure Debate</h2>
                    <label for="topic">Debate Topic:</label>
                    <input type="text" id="topic" value="{{ default_topic }}">
                    
                    <label for="rounds">Number of Rounds:</label>
                    <input type="number" id="rounds" min="1" max="5" value="{{ default_rounds }}">
                    
                    <button id="start-btn">Start Debate</button>
                </div>
                
                <div class="status-bar" id="status-bar">Ready to start debate</div>
                
                <div class="debate-log" id="debate-log">
                    <p>Configure your debate parameters and click Start Debate</p>
                </div>
                
                <div id="download-area" style="margin-top: 20px; display: none;">
                    <button id="download-btn">Download Transcript</button>
                    <button id="new-debate-btn" style="margin-left: 10px; background: #f0ad4e;">New Debate</button>
                </div>
                
                <script>
                    let debateId = null;
                    let pollingInterval = null;
                    
                    document.getElementById('start-btn').addEventListener('click', function() {
                        const topic = document.getElementById('topic').value;
                        const rounds = document.getElementById('rounds').value;
                        
                        if (!topic) {
                            alert("Please enter a debate topic");
                            return;
                        }
                        
                        // Update status
                        document.getElementById('status-bar').textContent = "Starting debate...";
                        document.getElementById('start-btn').disabled = true;
                        
                        // Clear previous debate
                        document.getElementById('debate-log').innerHTML = '<p>Initializing debate...</p>';
                        document.getElementById('download-area').style.display = 'none';
                        
                        // Start new debate
                        fetch('/start_debate', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                topic: topic,
                                rounds: rounds
                            }),
                        })
                        .then(response => response.json())
                        .then(data => {
                            debateId = data.debate_id;
                            
                            // Start polling for updates
                            pollingInterval = setInterval(pollDebateStatus, 1000);
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            document.getElementById('status-bar').textContent = "Error starting debate";
                            document.getElementById('start-btn').disabled = false;
                        });
                    });
                    
                    function pollDebateStatus() {
                        if (!debateId) return;
                        
                        fetch(`/debate_status/${debateId}`)
                        .then(response => response.json())
                        .then(data => {
                            updateDebateLog(data);
                            
                            // Update status bar
                            if (data.status === 'running') {
                                document.getElementById('status-bar').textContent = "Debate in progress...";
                            } else if (data.status === 'completed') {
                                document.getElementById('status-bar').textContent = "Debate completed!";
                                document.getElementById('start-btn').disabled = false;
                                document.getElementById('download-area').style.display = 'block';
                                clearInterval(pollingInterval);
                            } else if (data.status === 'error') {
                                document.getElementById('status-bar').textContent = "Error occurred during debate";
                                document.getElementById('start-btn').disabled = false;
                                clearInterval(pollingInterval);
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                        });
                    }
                    
                    function updateDebateLog(data) {
                        const logElement = document.getElementById('debate-log');
                        logElement.innerHTML = '';
                        
                        data.messages.forEach(msg => {
                            const messageDiv = document.createElement('div');
                            
                            // Style based on role
                            if (msg.role === 'ProAgent') {
                                messageDiv.classList.add('pro');
                                messageDiv.innerHTML = `<strong>PRO:</strong> ${msg.content}`;
                            } else if (msg.role === 'ConAgent') {
                                messageDiv.classList.add('con');
                                messageDiv.innerHTML = `<strong>CON:</strong> ${msg.content}`;
                            } else if (msg.role === 'Moderator') {
                                messageDiv.classList.add('moderator');
                                messageDiv.innerHTML = `<strong>MODERATOR:</strong> ${msg.content}`;
                            } else if (msg.role === 'system') {
                                messageDiv.classList.add('system');
                                messageDiv.innerHTML = `${msg.content}`;
                            } else {
                                messageDiv.innerHTML = msg.content;
                            }
                            
                            logElement.appendChild(messageDiv);
                            
                            // Don't add horizontal rule after system messages
                            if (msg.role !== 'system') {
                                logElement.appendChild(document.createElement('hr'));
                            }
                        });
                        
                        // Auto-scroll to bottom
                        logElement.scrollTop = logElement.scrollHeight;
                    }
                    
                    document.getElementById('download-area').addEventListener('click', function(e) {
                        if (e.target.id === 'download-btn') {
                            if (!debateId) return;
                            window.location.href = `/download/${debateId}`;
                        } else if (e.target.id === 'new-debate-btn') {
                            // Reset for new debate
                            debateId = null;
                            document.getElementById('debate-log').innerHTML = '<p>Configure your debate parameters and click Start Debate</p>';
                            document.getElementById('download-area').style.display = 'none';
                            document.getElementById('status-bar').textContent = "Ready to start debate";
                        }
                    });
                </script>
            </body>
            </html>""")
    
    print(f"Starting web interface on http://127.0.0.1:5000")
    app.run(debug=True)