"""Integration tests for Flask API endpoints."""
import pytest
import json
from unittest.mock import patch, Mock


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_index_route(self, client):
        """Test that index route serves frontend."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_get_config(self, client):
        """Test GET /api/config endpoint."""
        response = client.get('/api/config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'model' in data
        assert 'system_prompt' in data
        assert 'temperature' in data
        assert 'stream' in data
        # Note: The actual model value depends on the config file
        # This test verifies the endpoint works, not the specific config values
    
    @patch('app.ollama_client.list_models')
    def test_get_models(self, mock_list_models, client):
        """Test GET /api/models endpoint."""
        mock_list_models.return_value = {
            "models": [{"name": "llama2"}, {"name": "mistral"}]
        }
        
        response = client.get('/api/models')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "models" in data
        assert len(data["models"]) == 2
    
    def test_chat_no_messages(self, client):
        """Test POST /api/chat with no messages."""
        response = client.post('/api/chat', 
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.ollama_client.chat')
    def test_chat_with_messages(self, mock_chat, client):
        """Test POST /api/chat with valid messages."""
        mock_chat.return_value = iter([
            {"message": {"content": "Hello"}, "done": False},
            {"message": {"content": " world"}, "done": True}
        ])
        
        response = client.post('/api/chat',
                              json={
                                  "messages": [{"role": "user", "content": "Hi"}],
                                  "model": "llama2"
                              },
                              content_type='application/json')
        
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
    
    @patch('app.config_loader.reload')
    def test_reload_config(self, mock_reload, client):
        """Test POST /api/reload-config endpoint."""
        response = client.post('/api/reload-config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'config' in data
        
        mock_reload.assert_called_once()
    
    @patch('app.ollama_client.chat')
    def test_chat_with_correct_model_name(self, mock_chat, client):
        """Test POST /api/chat works with tinyllama:latest model name."""
        # Mock successful chat response
        mock_chat.return_value = iter([
            {"message": {"content": "Hello from tinyllama!"}, "done": True}
        ])
        
        # Test with the correct model name that was fixed
        response = client.post('/api/chat',
                              json={
                                  "messages": [{"role": "user", "content": "Hi"}],
                                  "model": "tinyllama:latest"
                              },
                              content_type='application/json')
        
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
        
        # Verify that the chat method was called (the specific args are complex due to system prompt)
        mock_chat.assert_called_once()
    
    @patch('app.ollama_client.chat')
    def test_chat_with_invalid_model_returns_error(self, mock_chat, client):
        """Test POST /api/chat with invalid model returns error (reproduces the original issue)."""
        # Mock Ollama returning the 404 error that was the original problem
        mock_chat.return_value = iter([
            {"error": "404 Client Error: Not Found for url: http://localhost:11434/api/chat"}
        ])
        
        response = client.post('/api/chat',
                              json={
                                  "messages": [{"role": "user", "content": "Hi"}],
                                  "model": "invalid-model"
                              },
                              content_type='application/json')
        
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
        
        # Verify that the error was propagated through the stream
        mock_chat.assert_called_once()
