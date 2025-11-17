"""Jailbreak detection module for Ollama chat application."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from ollama_client import OllamaClient
from config_loader import ConfigLoader


@dataclass(frozen=True)
class JailbreakDetectionResult:
    """Result of jailbreak detection analysis."""
    is_jailbreak: bool
    detection_request: str
    model_response: str


class JailbreakDetector:
    """
    Detects potential jailbreak attempts in user prompts using AI model analysis.

    This class encapsulates the logic for identifying prompts that attempt to bypass
    security measures or coerce the AI into breaking its guidelines.
    """

    def __init__(self, ollama_client: OllamaClient, model_name: str, config_loader: ConfigLoader):
        """
        Initialize the jailbreak detector.

        Args:
            ollama_client: Client for communicating with Ollama API
            model_name: Name of the model to use for detection analysis
            config_loader: Configuration loader to get jailbreak prompt template

        Raises:
            ValueError: If jailbreak_prompt is not configured in the config
        """
        self._ollama_client = ollama_client
        self._model_name = model_name
        self._config_loader = config_loader
        
        # Validate that jailbreak detection is properly configured
        jailbreak_prompt = self._config_loader.get("jailbreak_prompt")
        if not jailbreak_prompt:
            raise ValueError(
                "Jailbreak detection is not configured. "
                "Please set 'jailbreak_prompt' in your config.json file to enable jailbreak detection."
            )
        
        self._jailbreak_prompt_template = jailbreak_prompt

    def detect_jailbreak(self, user_prompt: str) -> JailbreakDetectionResult:
        """
        Analyze a user prompt to detect potential jailbreak attempts.

        Args:
            user_prompt: The user's input prompt to analyze

        Returns:
            JailbreakDetectionResult containing detection outcome and analysis details
        """
        detection_request = self._create_detection_prompt(user_prompt)

        messages = [{"role": "user", "content": detection_request}]

        try:
            response = self._ollama_client.chat(
                model=self._model_name,
                messages=messages,
                stream=False
            )

            model_response = self._extract_response_content(response)
            is_jailbreak = self._analyze_response_for_jailbreak(model_response)

            return JailbreakDetectionResult(
                is_jailbreak=is_jailbreak,
                detection_request=detection_request,
                model_response=model_response
            )

        except Exception as e:
            # In case of API errors, err on the side of caution
            return JailbreakDetectionResult(
                is_jailbreak=False,  # Don't block legitimate requests due to errors
                detection_request=detection_request,
                model_response=f"Error during detection: {str(e)}"
            )

    def _create_detection_prompt(self, user_prompt: str) -> str:
        """
        Create a detection prompt that instructs the model to analyze the user prompt.

        Args:
            user_prompt: The user's input to analyze

        Returns:
            Formatted detection prompt for the model
        """
        return self._jailbreak_prompt_template.replace("\\user_prompt", user_prompt)

    def _extract_response_content(self, response: List[Dict[str, Any]]) -> str:
        """
        Extract the text content from the model's response.

        Args:
            response: Raw response from Ollama API

        Returns:
            Extracted text content or empty string if extraction fails
        """
        if not response:
            return ""

        try:
            return response[0].get("message", {}).get("content", "")
        except (IndexError, KeyError, TypeError):
            return ""

    def _analyze_response_for_jailbreak(self, model_response: str) -> bool:
        """
        Analyze the model's response to determine if a jailbreak was detected.

        Args:
            model_response: The model's analysis response

        Returns:
            True if jailbreak detected, False otherwise
        """
        normalized_response = model_response.strip().upper()
        return "JAILBREAK_DETECTED" in normalized_response