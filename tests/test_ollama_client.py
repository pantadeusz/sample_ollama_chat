"""Unit tests for OllamaClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ollama_client import OllamaClient


class TestOllamaClient:
    """Test cases for OllamaClient class."""

    def test_init(self):
        """Test client initialization."""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.api_url == "http://localhost:11434/api"

        custom_client = OllamaClient(base_url="http://custom:8080")
        assert custom_client.base_url == "http://custom:8080"
        assert custom_client.api_url == "http://custom:8080/api"

    @patch("ollama_client.requests.post")
    def test_chat_stream(self, mock_post):
        """Test streaming chat request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines = Mock(
            return_value=[
                b'{"message": {"content": "Hello"}, "done": false}',
                b'{"message": {"content": " world"}, "done": true}',
            ]
        )
        mock_post.return_value = mock_response

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hi"}]

        responses = list(client.chat("llama2", messages, stream=True))

        assert len(responses) == 2
        assert responses[0]["message"]["content"] == "Hello"
        assert responses[1]["done"] is True

        mock_post.assert_called_once()

    @patch("ollama_client.requests.post")
    def test_chat_non_stream(self, mock_post):
        """Test non-streaming chat request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={"message": {"content": "Response"}, "done": True}
        )
        mock_post.return_value = mock_response

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hi"}]

        responses = list(client.chat("llama2", messages, stream=False))

        assert len(responses) == 1
        assert responses[0]["message"]["content"] == "Response"

    @patch("ollama_client.requests.post")
    def test_chat_error(self, mock_post):
        """Test chat request with error."""
        mock_post.side_effect = Exception("Connection error")

        client = OllamaClient()
        messages = [{"role": "user", "content": "Hi"}]

        responses = list(client.chat("llama2", messages))

        assert len(responses) == 1
        assert "error" in responses[0]

    @patch("ollama_client.requests.get")
    def test_list_models(self, mock_get):
        """Test listing available models."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={"models": [{"name": "llama2"}, {"name": "mistral"}]}
        )
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models()

        assert "models" in models
        assert len(models["models"]) == 2

        mock_get.assert_called_once()

    @patch("ollama_client.requests.get")
    def test_list_models_error(self, mock_get):
        """Test list models with error."""
        mock_get.side_effect = Exception("Connection error")

        client = OllamaClient()
        result = client.list_models()

        assert "error" in result
