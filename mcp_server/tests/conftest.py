"""Pytest configuration for mcp_server tests."""

import os
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Fixture providing path to test data directory."""
    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Test data directory not found: {data_dir}. Please create the directory and add necessary test data files."
        )
    return data_dir


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

    def _parse_threshold(env_var: str, default: str, description: str) -> float:
        """Parse environment variable as float with clear error handling."""
        value = os.getenv(env_var, default)
        try:
            return float(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid {description} threshold in environment variable {env_var}: "
                f"'{value}' is not a valid float. Expected a numeric value like '1.0' or '0.5'."
            ) from e

    return {
        "prompt_loading": _parse_threshold("PERF_THRESHOLD_PROMPT_LOADING", "1.0", "prompt loading performance"),
        "attribute_access": _parse_threshold("PERF_THRESHOLD_ATTRIBUTE_ACCESS", "0.5", "attribute access performance"),
    }


# Enable async testing support for pytest
pytest_plugins = ("pytest_asyncio",)
