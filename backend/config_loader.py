"""Configuration loader for Ollama chat application."""
import json
import os
from typing import Dict, Any


class ConfigLoader:
    """Load and manage application configuration."""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            Dictionary with configuration
        """
        if not os.path.exists(self.config_path):
            return self.get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "model": "llama2",
            "ollama_url": "http://localhost:11434",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "stream": True
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self.load_config()
