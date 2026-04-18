"""
conftest.py — Shared pytest configuration and fixtures for ArenaMaxx test suite.

This module provides:
  - Shared test client fixture with in-memory SQLite database isolation.
  - Utility helpers for repeated assertion patterns.
  - Mock patches for external services (Firebase, Gemini) to ensure test isolation.
"""

from __future__ import annotations
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_firebase_for_tests():
    """
    Automatically patch Firebase to prevent real network calls during tests.
    Applied to every test automatically via autouse=True.
    """
    with patch('firebase_service._firebase_initialized', False), \
         patch('firebase_service._firestore_client', None):
        yield


@pytest.fixture(autouse=True)
def mock_gcp_logging():
    """
    Automatically suppress Google Cloud Logging client initialization in tests.
    Prevents test failures when GCP credentials are not available locally.
    """
    with patch('google.cloud.logging.Client') as mock_client:
        mock_client.return_value.setup_logging.return_value = None
        yield mock_client
