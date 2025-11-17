"""Pytest configuration and fixtures."""

import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
)

from app import app as flask_app


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the Flask application."""
    return app.test_cli_runner()
