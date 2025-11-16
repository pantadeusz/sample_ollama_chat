"""Flask backend for Ollama chat application."""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import logging
import datetime
from ollama_client import OllamaClient
from config_loader import ConfigLoader

# Set up logging
logger = logging.getLogger(__name__)


app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Load configuration
config_loader = ConfigLoader(config_path='../config/config.json')
ollama_client = OllamaClient(base_url=config_loader.get('ollama_url'))


@app.route('/')
def index():
    """Serve the frontend."""
    return app.send_static_file('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    return jsonify({
        'model': config_loader.get('model'),
        'system_prompt': config_loader.get('system_prompt'),
        'starter_message': config_loader.get('starter_message', 'Hello! I\'m ready to chat. Choose a model and send a message.'),
        'temperature': config_loader.get('temperature'),
        'stream': config_loader.get('stream')
    })


@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available Ollama models."""
    models = ollama_client.list_models()
    return jsonify(models)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    data = request.json
    messages = data.get('messages', [])
    model = data.get('model', config_loader.get('model'))
    stream = data.get('stream', config_loader.get('stream', True))
    
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400
    
    # Add system prompt if configured and not already present
    system_prompt = config_loader.get('system_prompt')
    if system_prompt:
        # Check if system prompt already exists
        has_system = messages and messages[0].get('role') == 'system'
        
        if not has_system:
            # For models that don't respect system prompts well (like Mistral),
            # we use a strong context injection approach
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            context_injection = {
                'role': 'user',
                'content': f'IMPORTANT INSTRUCTIONS: You must answer based ONLY on the following information. Do not use any other knowledge.\n\nToday is {current_date}.\n\n{system_prompt}\n\n---\n\nIMPORTANT: Answer questions directly and naturally. Never mention where the information came from (e.g., don\'t say "according to his CV", "based on the information", "from the context", etc.). Present all facts as if you know them directly. Be confident and conversational.'
            }
            acknowledgment = {
                'role': 'assistant', 
                'content': 'Understood. I will answer questions directly and naturally without referencing sources or mentioning where the information came from.'
            }
            
            # Insert at the beginning
            messages.insert(0, acknowledgment)
            messages.insert(0, context_injection)
    
    # Debug logging
    logger.info(f"Sending {len(messages)} messages to model {model}")
    logger.info(f"System prompt length: {len(system_prompt) if system_prompt else 0}")
    logger.info(f"Message roles: {[m.get('role') for m in messages]}")
    
    if stream:
        def generate():
            for chunk in ollama_client.chat(model, messages, stream=True):
                if 'error' in chunk:
                    yield f"data: {json.dumps(chunk)}\n\n"
                    break
                yield f"data: {json.dumps(chunk)}\n\n"
                if chunk.get('done', False):
                    break
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        responses = list(ollama_client.chat(model, messages, stream=False))
        if responses and 'error' in responses[0]:
            return jsonify(responses[0]), 500
        return jsonify(responses[0] if responses else {})


@app.route('/api/reload-config', methods=['POST'])
def reload_config():
    """Reload configuration from file."""
    config_loader.reload()
    return jsonify({'status': 'success', 'config': config_loader.config})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
