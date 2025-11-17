# Ollama Chat Application

Author: Tadeusz Puźniakowski

Generated using GitHub Copilot.

A simple chat interface for local Ollama API with pure JavaScript frontend and Python backend, featuring context-aware AI conversations with Markdown rendering and security protections.

## Requirements

- Python 3.8+
- Ollama installed locally and running
- At least one model downloaded in Ollama (e.g. `ollama pull llama3.1:8b`)

### Tested Models

The following models have been tested and work correctly:

```
NAME                   ID              SIZE
llama3.1:8b           various         ~4.7 GB
mistral:latest        various         ~4.1 GB
qwen2.5:7b           various         ~4.7 GB
smallthinker:latest   945eb1864589    3.6 GB
tinyllama:latest      2644915ede35    637 MB
```

### Installation

1. **Clone or download the project**

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Ensure Ollama is running locally**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If you don't have models, download one:
ollama pull llama3.1:8b
# or
ollama pull mistral
```

## Configuration

### Basic Configuration

1. **Copy the example configuration:**
```bash
cp config/config.example.json config/config.json
```

2. **Edit the `config/config.json` file** to configure the default model and other options:

```json
{
  "model": "llama3.1:8b",
  "ollama_url": "http://localhost:11434",
  "system_prompt": "You are a helpful AI assistant. Be polite, concise, and helpful.",
  "starter_message": "Hello! I'm ready to help you. What would you like to know?",
  "temperature": 0.7,
  "stream": true,
  "context_directory": "../context",
  "context_header": "--- Context Information ---\n\nIMPORTANT: Use the following information to answer questions accurately.\n\n",
  "context_footer": "\n\n--- End of Context ---\n\nSystem Instructions:\n\n"
}
```

### Configuration Options:

- **model**: Name of the Ollama model to use (e.g. "llama3.1:8b", "mistral", "qwen2.5:7b")
- **ollama_url**: URL to the local Ollama instance
- **system_prompt**: System prompt for the AI assistant
- **temperature**: Temperature parameter (0.0 - 1.0) - higher value = more creative responses
- **stream**: Whether to stream responses (true/false)
- **context_directory**: (optional) Path to directory with context files (.md)
- **context_header**: (optional) Header added before context
- **context_footer**: (optional) Footer added after context
- **starter_message**: (optional) Welcome message displayed to user

### Advanced: Adding Personal Context

The application supports automatic context loading from Markdown files, allowing you to create an AI assistant with specialized knowledge:

1. **Create a context directory:**
```bash
mkdir context
```

2. **Add .md files with information:**
```bash
# Example: context/cv.md, context/projects.md, context/publications.md
```

3. **Update config.json:**
```json
{
  "model": "mistral:latest",
  "context_directory": "../context",
  "context_header": "--- Context Information ---\n\nIMPORTANT: Use the following information to answer questions accurately.\n\n",
  "context_footer": "\n\n--- End of Context ---\n\nSystem Instructions:\n\n",
  "system_prompt": "You are an AI assistant with access to specialized knowledge..."
}
```

**Note:** The `context/` directory and `config/config.json` file are in `.gitignore` and will not be committed to the repository. This allows you to maintain privacy of personal information while sharing the code.

## Running

1. **Start the Flask backend**
```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

2. **Open your browser**

Navigate to `http://localhost:5000`

## Testing

The project includes unit and integration tests written in pytest.

### Run all tests:
```bash
pytest
```

### Run tests with code coverage:
```bash
pytest --cov=backend --cov-report=html
```

Coverage report will be generated in the `htmlcov/` folder.

### Run specific test files:
```bash
pytest tests/test_config_loader.py
pytest tests/test_ollama_client.py
pytest tests/test_api.py
```

## Project Structure

```
sample_ollama_chat/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # Main Flask application
│   ├── ollama_client.py       # Ollama API client
│   └── config_loader.py       # Configuration loader
├── frontend/
│   ├── index.html             # Main HTML
│   ├── app.js                 # Chat logic (pure JS)
│   └── styles.css             # CSS styles
├── context/                   # Context files (ignored by git)
│   ├── cv_clean.md           # CV information
│   ├── opensource.md         # Open-source portfolio
│   └── *.md                  # Other context files
├── config/
│   ├── config.json            # Active configuration (ignored)
│   └── config.example.json    # Example configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration
│   ├── test_config_loader.py  # Config loader tests
│   ├── test_ollama_client.py  # Ollama client tests
│   └── test_api.py            # API endpoint tests
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## API Endpoints

### GET `/api/config`
Returns current configuration (starter message and streaming settings).

### POST `/api/chat`
Sends a message to Ollama and returns the response.

**Request body:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

**Security Features:**
- Multi-layer prompt injection protection
- Dynamic date injection for context awareness
- Immutable system configuration with absolute security rules
- Confidential context handling

### POST `/api/reload-config`
Reloads configuration from file without server restart.

## Features

- Pure JavaScript (ECMAScript) + HTML5 frontend
- Real-time streaming responses
- Configuration via JSON file
- Context-aware conversations with Markdown file support
- **Markdown rendering**: Bold, italics, links, and code blocks
- Security protections against prompt injection
- Responsive interface
- Typing indicator
- Conversation history
- Error handling
- Code block formatting with syntax highlighting
- Unit and integration tests
- MIT License

## Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
ollama serve

# In a new terminal check status
curl http://localhost:11434/api/tags
```

### Model not available
```bash
# See list of installed models
ollama list

# Download a new model
ollama pull llama3.1:8b
```

### CORS errors
Make sure `flask-cors` is installed:
```bash
pip install flask-cors
```

### Port occupied
Change the port in `backend/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to different port
```

## License

MIT License

Copyright (c) 2025 Tadeusz Puźniakowski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

If you want to develop the project further:
1. Add more configuration options
2. Implement chat history saving
3. Add support for multiple conversations
4. Add conversation export to file
5. Implement user authentication

I'm open to PRs. All change requests should be discussed as issues first.

## Support

For issues check:
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MDN Web Docs](https://developer.mozilla.org/) for JavaScript
