"""Configuration loader for Ollama chat application."""

import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Enhance system_prompt with context if available
                if "context_directory" in config:
                    context_dir = (
                        Path(self.config_path).parent / config["context_directory"]
                    )
                    if context_dir.exists() and context_dir.is_dir():
                        context_text = self._load_context(context_dir)
                        if context_text:
                            context_header = config.get("context_header", "")
                            context_footer = config.get("context_footer", "\n\n")
                            config["system_prompt"] = (
                                context_header
                                + context_text
                                + context_footer
                                + "\n\nSYSTEM PROMPT:\n\n"
                                + config["system_prompt"]
                            )
                return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()

    def _load_context(self, context_dir: Path) -> str:
        """
        Load context from .md files in the specified directory.

        Args:
            context_dir: Path to the context directory

        Returns:
            Concatenated context text
        """
        context_parts = []
        for file_path in sorted(context_dir.glob("*.md")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        filename = file_path.name
                        context_parts.append(f"### File: {filename}\n\n{content}")
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        return "\n\n".join(context_parts)

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
            "stream": True,
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
