"""Unit tests for ConfigLoader."""

import pytest
import json
import os
import tempfile
from config_loader import ConfigLoader


class TestConfigLoader:
    """Test cases for ConfigLoader class."""

    def test_default_config(self):
        """Test that default config is returned when file doesn't exist."""
        loader = ConfigLoader(config_path="nonexistent.json")
        config = loader.config

        assert "model" in config
        assert "ollama_url" in config
        assert "system_prompt" in config
        assert config["model"] == "llama2"

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        test_config = {
            "model": "test-model",
            "ollama_url": "http://test:1234",
            "system_prompt": "Test prompt",
            "temperature": 0.5,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name

        try:
            loader = ConfigLoader(config_path=temp_path)

            assert loader.get("model") == "test-model"
            assert loader.get("ollama_url") == "http://test:1234"
            assert loader.get("temperature") == 0.5
        finally:
            os.unlink(temp_path)

    def test_get_with_default(self):
        """Test get method with default value."""
        loader = ConfigLoader(config_path="nonexistent.json")

        value = loader.get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_config_path_resolution(self):
        """Test that config path is correctly resolved."""
        # Test with absolute path
        abs_path = os.path.abspath("test_config.json")
        test_config = {"model": "test-model", "test": True}

        with open(abs_path, "w") as f:
            json.dump(test_config, f)

        try:
            loader = ConfigLoader(config_path=abs_path)
            assert loader.get("model") == "test-model"
            assert loader.get("test") == True
        finally:
            os.unlink(abs_path)

    def test_relative_config_path(self):
        """Test config loading with relative path."""
        # Create a test config in a subdirectory
        os.makedirs("test_subdir", exist_ok=True)
        config_path = "test_subdir/test_config.json"
        test_config = {"model": "relative-model", "path_test": True}

        with open(config_path, "w") as f:
            json.dump(test_config, f)

        try:
            loader = ConfigLoader(config_path=config_path)
            assert loader.get("model") == "relative-model"
            assert loader.get("path_test") == True
        finally:
            os.unlink(config_path)
            os.rmdir("test_subdir")

    def test_reload_config(self):
        """Test reloading configuration."""
        test_config = {"model": "initial-model", "ollama_url": "http://localhost:11434"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name

        try:
            loader = ConfigLoader(config_path=temp_path)
            assert loader.get("model") == "initial-model"

            # Update file
            updated_config = {
                "model": "updated-model",
                "ollama_url": "http://localhost:11434",
            }
            with open(temp_path, "w") as f:
                json.dump(updated_config, f)

            loader.reload()
            assert loader.get("model") == "updated-model"
        finally:
            os.unlink(temp_path)

    def test_invalid_json(self):
        """Test that invalid JSON returns default config."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            loader = ConfigLoader(config_path=temp_path)

            # Should fall back to default config
            assert loader.get("model") == "llama2"
        finally:
            os.unlink(temp_path)

    def test_load_prompts_from_directory(self):
        """Test loading prompts from a prompts_directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a prompts subdirectory
            prompts_dir = os.path.join(temp_dir, "prompts")
            os.makedirs(prompts_dir)

            # Create prompt files
            with open(os.path.join(prompts_dir, "system_prompt.md"), "w") as f:
                f.write("Test system prompt")
            with open(os.path.join(prompts_dir, "starter_message.md"), "w") as f:
                f.write("Test starter message")

            # Create config file that references prompts directory
            config_path = os.path.join(temp_dir, "config.json")
            test_config = {
                "model": "test-model",
                "ollama_url": "http://localhost:11434",
                "prompts_directory": "./prompts",
            }
            with open(config_path, "w") as f:
                json.dump(test_config, f)

            # Load config
            loader = ConfigLoader(config_path=config_path)

            # Verify prompts were loaded from directory
            assert loader.get("system_prompt") == "Test system prompt"
            assert loader.get("starter_message") == "Test starter message"
            assert loader.get("model") == "test-model"

    def test_fallback_to_config_example(self):
        """Test fallback to config.example.json when config.json doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config.example.json
            example_config = {
                "model": "example-model",
                "ollama_url": "http://localhost:11434",
                "temperature": 0.7,
            }
            example_path = os.path.join(temp_dir, "config.example.json")
            with open(example_path, "w") as f:
                json.dump(example_config, f)

            # Try to load config.json (which doesn't exist)
            config_path = os.path.join(temp_dir, "config.json")
            loader = ConfigLoader(config_path=config_path)

            # Should have loaded config.example.json instead
            assert loader.get("model") == "example-model"
            assert loader.get("ollama_url") == "http://localhost:11434"
            assert loader.get("temperature") == 0.7
