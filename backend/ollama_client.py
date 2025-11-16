"""Client for interacting with Ollama API."""
import requests
import json
from typing import Generator, Dict, Any


class OllamaClient:
    """Client to communicate with local Ollama instance."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL of Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def chat(self, model: str, messages: list, stream: bool = True) -> Generator[Dict[str, Any], None, None]:
        """
        Send chat request to Ollama.
        
        Args:
            model: Model name to use
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream responses
            
        Yields:
            Response chunks from Ollama
        """
        url = f"{self.api_url}/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "num_ctx": 16384,  # Increase context window to handle large prompts
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(url, json=payload, stream=stream, timeout=60)
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        yield json.loads(line.decode('utf-8'))
            else:
                yield response.json()
                
        except Exception as e:
            yield {"error": str(e)}
    
    def list_models(self) -> Dict[str, Any]:
        """
        Get list of available models.
        
        Returns:
            Dictionary with available models
        """
        url = f"{self.api_url}/tags"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
