from flask import Flask, session, request, jsonify
import uuid
import os
import json
from datetime import datetime
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Generate a secure random key for session encryption
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Directory to store session data
SESSION_DIR = "session_data"
os.makedirs(SESSION_DIR, exist_ok=True)

def get_session_file_path(session_id):
    """Get the file path for a session data file."""
    return os.path.join(SESSION_DIR, f"{session_id}.json")

def save_session_data(session_id, data):
    """Save session data to a file."""
    file_path = get_session_file_path(session_id)
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error saving session data: {e}")

def load_session_data(session_id):
    """Load session data from a file."""
    file_path = get_session_file_path(session_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
    return {"chat_history": [], "metadata": {}}

@app.route('/get_session_id', methods=['GET'])
def get_session_id():
    """Get or create a session ID for the client."""
    if 'session_id' not in session:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Initialize session data
        session_data = {
            "chat_history": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()
            }
        }
        save_session_data(session_id, session_data)
        logger.info(f"Created new session: {session_id}")
    else:
        session_id = session['session_id']
        
    return jsonify({
        'session_id': session_id,
        'status': 'active'
    })

@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    """Get the chat history for the current session."""
    session_id = session.get('session_id')
    if not session_id:
        # Initialize a new session if none exists
        session_data = requests.get('http://localhost:5000/get_session_id').json()
        session_id = session_data['session_id']
    
    # Get history and update last activity
    session_data = load_session_data(session_id)
    session_data["metadata"]["last_activity"] = datetime.now().isoformat()
    save_session_data(session_id, session_data)
    
    return jsonify({
        'session_id': session_id,
        'chat_history': session_data["chat_history"]
    })

@app.route('/update_chat_history', methods=['POST'])
def update_chat_history():
    """Add a message to the chat history."""
    session_id = session.get('session_id')
    if not session_id:
        # Return empty history if no session
        return jsonify({
            'session_id': None,
            'chat_history': []
        })
    
    # Get current data
    session_data = load_session_data(session_id)
    
    # Add the new message
    new_message = request.json
    if new_message:
        # Add timestamp to messages
        new_message["timestamp"] = datetime.now().isoformat()
        session_data["chat_history"].append(new_message)
        session_data["metadata"]["last_activity"] = datetime.now().isoformat()
        session_data["metadata"]["message_count"] = len(session_data["chat_history"])
        
        # Save updated data
        save_session_data(session_id, session_data)
        logger.info(f"Added message to session {session_id}")
    
    return jsonify({
        'session_id': session_id,
        'chat_history': session_data["chat_history"]
    })

@app.route('/clear_chat_history', methods=['POST'])
def clear_chat_history():
    """Clear the chat history for the current session."""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({
            'session_id': None,
            'status': 'no_session',
            'chat_history': []
        })
    
    # Get current metadata
    session_data = load_session_data(session_id)
    metadata = session_data["metadata"]
    
    # Clear chat history but keep metadata
    session_data = {
        "chat_history": [],
        "metadata": {
            **metadata,
            "last_cleared": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0
        }
    }
    
    save_session_data(session_id, session_data)
    logger.info(f"Cleared chat history for session {session_id}")
    
    return jsonify({
        'session_id': session_id,
        'status': 'cleared',
        'chat_history': []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)