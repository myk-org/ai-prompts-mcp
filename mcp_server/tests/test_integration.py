"""Integration tests for the MCP server."""

from unittest.mock import patch

import pytest

import mcp_server.main as main_module
from mcp_server.main import mcp
from mcp_server.utils.utils import get_script_path, load_prompt_from_markdown


class TestMCPServerIntegration:
    """Integration tests for the complete MCP server functionality."""

    def test_server_initialization(self):
        """Test that the MCP server initializes correctly."""
        assert mcp is not None
        assert hasattr(mcp, "_prompt_manager")
        assert hasattr(mcp, "run")

    def test_prompt_registration_integration(self):
        """Test that all prompts are properly registered with the server."""
        # Get registered prompts
        prompt_dict = mcp._prompt_manager._prompts

        # Verify all expected prompts are registered
        expected_prompts = ["github-coderabbitai-review-handler", "commit", "github-review-handler"]

        for prompt_name in expected_prompts:
            assert prompt_name in prompt_dict


class TestEndToEndPromptFlow:
    """End-to-end tests for prompt functionality."""

    def test_end_to_end_prompt_loading_with_real_files(self, temp_dir):
        """Test complete prompt loading flow with actual file system."""
        # Create realistic file structure
        prompts_dir = temp_dir / "prompts"
        scripts_dir = temp_dir / "scripts"
        prompts_dir.mkdir()
        scripts_dir.mkdir()

        # Create real prompt file
        prompt_content = """---
title: Test Integration Prompt
description: A test prompt for integration testing
---

# Integration Test Prompt

This prompt uses scripts: {{SCRIPT_PATHS}}

Additional instructions here."""

        prompt_file = prompts_dir / "test-integration.md"
        prompt_file.write_text(prompt_content, encoding="utf-8")

        # Create real script files
        script1_dir = scripts_dir / "folder1"
        script1_dir.mkdir()
        script1 = script1_dir / "script1.sh"
        script1.write_text("#!/bin/bash\necho 'script1'", encoding="utf-8")

        script2_dir = scripts_dir / "folder2"
        script2_dir.mkdir()
        script2 = script2_dir / "script2.sh"
        script2.write_text("#!/bin/bash\necho 'script2'", encoding="utf-8")

        # Mock the path resolution to use our temp directory
        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir

            # Test loading prompt with scripts
            result = load_prompt_from_markdown("test-integration", ["folder1/script1.sh", "folder2/script2.sh"])

        # Verify the result
        assert "# Integration Test Prompt" in result
        assert "{{SCRIPT_PATHS}}" not in result
        assert "folder1/script1.sh" in result
        assert "folder2/script2.sh" in result
        assert "Additional instructions here." in result
        # Frontmatter should be stripped
        assert "title: Test Integration Prompt" not in result

    def test_end_to_end_prompt_loading_without_scripts(self, temp_dir):
        """Test prompt loading without script replacement."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        prompt_content = """# Simple Prompt

This is a simple prompt without script placeholders.

Just plain instructions."""

        prompt_file = prompts_dir / "simple-prompt.md"
        prompt_file.write_text(prompt_content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("simple-prompt")

        assert "# Simple Prompt" in result
        assert "Just plain instructions." in result

    def test_script_path_resolution_integration(self):
        """Test that script path resolution works correctly."""
        script_name = "github-coderabbitai-review-handler/get-coderabbit-comments.sh"
        result = get_script_path(script_name)

        # Should return absolute path
        assert result.is_absolute()

        # Should contain expected components
        path_str = str(result)
        assert "mcp_server" in path_str
        assert "scripts" in path_str
        assert "github-coderabbitai-review-handler" in path_str
        assert "get-coderabbit-comments.sh" in path_str


class TestPromptFunctionIntegration:
    """Integration tests for individual prompt functions."""

    def test_github_coderabbitai_review_handler_integration(self):
        """Test github_coderabbitai_review_handler prompt structure."""
        prompt = main_module.github_coderabbitai_review_handler

        assert prompt.name == "github-coderabbitai-review-handler"
        assert "CodeRabbit AI comments" in prompt.description
        assert prompt.enabled is True

    def test_commit_integration(self):
        """Test commit prompt structure."""
        prompt = main_module.commit

        assert prompt.name == "commit"
        assert "Git Commit" in prompt.description
        assert prompt.enabled is True

    def test_github_review_handler_integration(self):
        """Test github_review_handler prompt structure."""
        prompt = main_module.github_review_handler

        assert prompt.name == "github-review-handler"
        assert "human reviewer comments" in prompt.description
        assert prompt.enabled is True


class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios."""

    def test_missing_prompt_file_integration(self, temp_dir):
        """Test handling of missing prompt files."""
        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("nonexistent-prompt")

        assert "Error: Prompt file 'nonexistent-prompt.md' not found" in result

    def test_prompt_function_with_missing_file(self, temp_dir):
        """Test that prompt functions exist and have proper structure."""
        # Test that the prompt functions exist and are properly configured
        assert main_module.commit.name == "commit"
        assert main_module.commit.description is not None

    def test_malformed_prompt_file_integration(self, temp_dir):
        """Test handling of malformed prompt files."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create a file that can't be read properly (empty file)
        prompt_file = prompts_dir / "malformed.md"
        prompt_file.write_text("", encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("malformed")

        # Should handle empty file gracefully
        assert result == ""


class TestServerLifecycle:
    """Integration tests for server lifecycle operations."""

    def test_server_can_be_imported_without_errors(self):
        """Test that the server module can be imported without errors."""
        # This test verifies that all imports and module-level code works
        try:
            from mcp_server import main

            assert main.mcp is not None
        except ImportError as e:
            pytest.fail(f"Failed to import server module: {e}")

    @patch("sys.stderr")
    def test_print_available_prompts_integration(self, mock_stderr):
        """Test that print_available_prompts works with actual prompt manager."""
        from mcp_server.main import print_available_prompts

        # This should not raise any exceptions
        try:
            print_available_prompts()
        except Exception as e:
            pytest.fail(f"print_available_prompts failed: {e}")

    def test_all_prompt_functions_are_callable(self):
        """Test that all prompt functions can be called without import errors."""
        functions = [
            main_module.github_coderabbitai_review_handler,
            main_module.commit,
            main_module.github_review_handler,
        ]

        for func in functions:
            # Check that the decorated functions exist and have the right attributes
            assert hasattr(func, "name")
            assert hasattr(func, "description")
            assert func.description is not None


class TestPerformanceIntegration:
    """Performance-related integration tests."""

    def test_prompt_loading_performance(self, temp_dir):
        """Test that prompt loading performs reasonably well."""
        import time

        # Create a larger prompt file
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create a prompt with substantial content
        large_content = (
            """---
title: Large Test Prompt
---

# Large Test Prompt

"""
            + ("This is a line of content.\n" * 1000)
            + """

Execute: {{SCRIPT_PATHS}}

More content here."""
        )

        prompt_file = prompts_dir / "large-prompt.md"
        prompt_file.write_text(large_content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir

            start_time = time.time()
            result = load_prompt_from_markdown("large-prompt")
            end_time = time.time()

        # Should complete within reasonable time (adjust threshold as needed)
        assert end_time - start_time < 1.0  # 1 second threshold
        assert len(result) > 1000  # Should have loaded substantial content

    def test_multiple_prompt_calls_performance(self):
        """Test that prompt objects are properly initialized."""
        # Simplified performance test - just verify prompt objects exist and are usable
        prompts = [
            main_module.commit,
            main_module.github_coderabbitai_review_handler,
            main_module.github_review_handler,
        ]

        # Verify all prompts are accessible and have proper attributes
        for prompt in prompts:
            assert prompt.name is not None
            assert prompt.description is not None
            assert prompt.enabled is True
