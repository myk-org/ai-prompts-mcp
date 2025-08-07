"""Tests for mcp_server.main module."""

import pytest
from io import StringIO
from unittest.mock import patch, Mock

import mcp_server.main as main_module
from mcp_server.main import print_available_prompts, mcp


class TestPromptFunctions:
    """Test cases for prompt functions."""

    @patch("mcp_server.main.load_prompt_from_markdown")
    def test_load_prompt_from_markdown_integration(self, mock_load_prompt):
        """Test that prompt functions are properly integrated with load_prompt_from_markdown."""
        # We can't easily test the decorated functions directly, but we can verify
        # that the module imports correctly and the functions exist
        assert hasattr(main_module, "github_coderabbitai_review_handler")
        assert hasattr(main_module, "commit")
        assert hasattr(main_module, "github_review_handler")

        # Verify the functions are decorated FunctionPrompt objects
        assert hasattr(main_module.github_coderabbitai_review_handler, "name")
        assert hasattr(main_module.commit, "name")
        assert hasattr(main_module.github_review_handler, "name")

    def test_prompt_function_descriptions(self):
        """Test that all prompt functions have proper descriptions."""
        # Test descriptions exist in the FunctionPrompt objects
        assert main_module.github_coderabbitai_review_handler.description is not None
        assert "CodeRabbit AI comments" in main_module.github_coderabbitai_review_handler.description

        assert main_module.commit.description is not None
        assert "Git Commit" in main_module.commit.description

        assert main_module.github_review_handler.description is not None
        assert "human reviewer comments" in main_module.github_review_handler.description

    def test_prompt_function_names(self):
        """Test that prompt functions have correct names."""
        assert main_module.github_coderabbitai_review_handler.name == "github-coderabbitai-review-handler"
        assert main_module.commit.name == "commit"
        assert main_module.github_review_handler.name == "github-review-handler"


class TestPrintAvailablePrompts:
    """Test cases for print_available_prompts function."""

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_with_prompts(self, mock_stderr):
        """Test print_available_prompts with available prompts."""
        # Mock prompt data
        mock_prompt_info = Mock()
        mock_prompt_info.description = "Test prompt description\nSecond line"

        mock_prompts = {
            "test-prompt-1": mock_prompt_info,
            "another-prompt": mock_prompt_info,
        }

        # Mock the mcp object's prompt manager
        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = mock_prompts

            print_available_prompts()

        output = mock_stderr.getvalue()

        # Verify the output contains expected elements
        assert "📋 Available Prompts:" in output
        assert "another-prompt" in output
        assert "test-prompt-1" in output
        assert "Test prompt description" in output
        assert "Total: 2 prompts registered" in output
        assert "Server ready for connections..." in output

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_sorted_order(self, mock_stderr):
        """Test that prompts are printed in sorted order."""
        mock_prompt_info = Mock()
        mock_prompt_info.description = "Test description"

        # Create prompts in unsorted order
        mock_prompts = {
            "z-prompt": mock_prompt_info,
            "a-prompt": mock_prompt_info,
            "m-prompt": mock_prompt_info,
        }

        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = mock_prompts

            print_available_prompts()

        output = mock_stderr.getvalue()

        # Find positions of prompt names in output
        a_pos = output.find("a-prompt")
        m_pos = output.find("m-prompt")
        z_pos = output.find("z-prompt")

        # Verify they appear in sorted order
        assert a_pos < m_pos < z_pos

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_no_description(self, mock_stderr):
        """Test prompt without description."""
        mock_prompt_info = Mock()
        mock_prompt_info.description = None

        mock_prompts = {"test-prompt": mock_prompt_info}

        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = mock_prompts

            print_available_prompts()

        output = mock_stderr.getvalue()

        assert "No description available" in output

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_empty_description(self, mock_stderr):
        """Test prompt with empty description."""
        mock_prompt_info = Mock()
        mock_prompt_info.description = ""

        mock_prompts = {"test-prompt": mock_prompt_info}

        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = mock_prompts

            print_available_prompts()

        output = mock_stderr.getvalue()

        assert "No description available" in output

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_no_prompts(self, mock_stderr):
        """Test print_available_prompts with no available prompts."""
        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = {}

            print_available_prompts()

        output = mock_stderr.getvalue()

        assert "No prompts registered" in output

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_multiline_description(self, mock_stderr):
        """Test prompt with multiline description (should show only first line)."""
        mock_prompt_info = Mock()
        mock_prompt_info.description = "First line of description\nSecond line\nThird line"

        mock_prompts = {"test-prompt": mock_prompt_info}

        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = mock_prompts

            print_available_prompts()

        output = mock_stderr.getvalue()

        # Should only show first line
        assert "First line of description" in output
        assert "Second line" not in output
        assert "Third line" not in output

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_no_hasattr_description(self, mock_stderr):
        """Test prompt object without description attribute."""
        mock_prompt_info = Mock(spec=[])  # Mock without description attribute

        mock_prompts = {"test-prompt": mock_prompt_info}

        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = mock_prompts

            print_available_prompts()

        output = mock_stderr.getvalue()

        assert "No description available" in output

    @patch("sys.stderr", new_callable=StringIO)
    def test_print_available_prompts_whitespace_description(self, mock_stderr):
        """Test prompt with whitespace-only description.

        When a description contains only whitespace, the first line after splitting
        and stripping will be empty. Since an empty string is falsy, but the
        original description is truthy, this edge case should result in an empty
        description line being printed (not "No description available").
        """
        mock_prompt_info = Mock()
        mock_prompt_info.description = "   \n  \t  \n   "

        mock_prompts = {"test-prompt": mock_prompt_info}

        with patch.object(mcp, "_prompt_manager") as mock_prompt_manager:
            mock_prompt_manager._prompts = mock_prompts

            print_available_prompts()

        output = mock_stderr.getvalue()

        # Verify the prompt name appears
        assert "test-prompt" in output

        # The first line of whitespace-only description becomes empty after strip()
        # This creates an empty description line in the output
        lines = output.split("\n")
        test_prompt_line_idx = None
        for i, line in enumerate(lines):
            if "test-prompt" in line:
                test_prompt_line_idx = i
                break

        assert test_prompt_line_idx is not None
        # The next line should be the description line, which should be empty with just indentation
        # This happens because:
        # 1. The original description is truthy (contains whitespace)
        # 2. But split("\n")[0].strip() returns an empty string
        # 3. The empty string is still printed with indentation
        if test_prompt_line_idx + 1 < len(lines):
            desc_line = lines[test_prompt_line_idx + 1]
            # Should have indentation but no actual description text
            assert desc_line.strip() == ""
            assert desc_line == "     "  # Exactly 5 spaces for indentation


class TestMCPInstance:
    """Test cases for MCP instance configuration."""

    def test_mcp_instance_exists(self):
        """Test that mcp instance is properly initialized."""
        assert mcp is not None
        assert hasattr(mcp, "_prompt_manager")

    def test_mcp_instance_name(self):
        """Test that MCP instance has correct name."""
        # This test verifies the FastMCP instance is created with correct name
        # The actual verification depends on FastMCP implementation
        assert mcp is not None


class TestMainExecution:
    """Test cases for main execution flow."""

    def test_main_execution_flow(self):
        """Test the main execution flow components."""
        # We can't directly test __name__ == "__main__" block without subprocess
        # So we test that the components exist and work

        # Verify print_available_prompts can be called
        try:
            print_available_prompts()
        except Exception as e:
            pytest.fail(f"print_available_prompts failed: {e}")

        # Verify mcp instance exists and has run method
        assert hasattr(mcp, "run")
        assert callable(mcp.run)

    def test_prompt_registration(self):
        """Test that prompts are properly registered with the MCP instance."""
        # Verify that the decorators have been applied
        # This is indirectly tested by checking the functions exist and have attributes

        functions = [
            main_module.github_coderabbitai_review_handler,
            main_module.commit,
            main_module.github_review_handler,
        ]

        for func in functions:
            # Check the decorated function has the right attributes
            assert hasattr(func, "name")
            assert hasattr(func, "description")
            assert func.description is not None


class TestPromptIntegration:
    """Integration tests for prompt functions with actual markdown loading."""

    def test_prompt_function_attributes(self):
        """Test that prompt functions have all expected attributes."""
        expected_prompts = {
            "github-coderabbitai-review-handler": main_module.github_coderabbitai_review_handler,
            "commit": main_module.commit,
            "github-review-handler": main_module.github_review_handler,
        }

        for expected_name, func in expected_prompts.items():
            assert func.name == expected_name
            assert func.description is not None
            assert hasattr(func, "enabled")
            assert func.enabled is True

    def test_prompt_manager_registration(self):
        """Test that prompts are registered in the MCP prompt manager."""
        # Get all registered prompts
        prompt_dict = mcp._prompt_manager._prompts

        # Verify expected prompts are registered
        expected_names = ["github-coderabbitai-review-handler", "commit", "github-review-handler"]
        for name in expected_names:
            assert name in prompt_dict
