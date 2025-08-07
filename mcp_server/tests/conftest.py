"""Pytest configuration for mcp_server tests."""

import os
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Fixture providing path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def performance_thresholds():
    """Fixture providing configurable performance thresholds for tests.

    Thresholds can be overridden via environment variables:
    - PERF_THRESHOLD_PROMPT_LOADING: for prompt loading performance (default: 1.0s)
    - PERF_THRESHOLD_ATTRIBUTE_ACCESS: for attribute access performance (default: 0.5s)
    """
    return {
        "prompt_loading": float(os.getenv("PERF_THRESHOLD_PROMPT_LOADING", "1.0")),
        "attribute_access": float(os.getenv("PERF_THRESHOLD_ATTRIBUTE_ACCESS", "0.5")),
    }


# Enable async testing support for pytest
pytest_plugins = ("pytest_asyncio",)
