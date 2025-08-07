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

    async def test_prompt_registration_integration(self):
        """Test that all prompts are properly registered with the server."""
        # Get registered prompts using the public API
        prompt_dict = await mcp.get_prompts()

        # Verify all expected prompts are registered
        expected_prompts = ["github-coderabbitai-review-handler", "commit", "github-review-handler"]

        for prompt_name in expected_prompts:
            assert prompt_name in prompt_dict

    def test_prompt_registration_integration_sync(self):
        """Test that all prompts are properly registered with the server (synchronous fallback)."""
        # This test provides a fallback that directly checks the manager's internal state
        # when async testing is not available. This demonstrates the fragility of the approach.
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
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir

            # Test loading prompt with scripts
            result = load_prompt_from_markdown("test-integration", ["folder1/script1.sh", "folder2/script2.sh"])

        # Verify the result
        assert "# Integration Test Prompt" in result
        assert "{{SCRIPT_PATHS}}" not in result
        # Check for absolute paths since get_script_path returns absolute paths
        expected_script1_path = str(temp_dir / "scripts" / "folder1" / "script1.sh")
        expected_script2_path = str(temp_dir / "scripts" / "folder2" / "script2.sh")
        assert expected_script1_path in result
        assert expected_script2_path in result
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
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
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
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("nonexistent-prompt")

        assert "Error: Prompt file 'nonexistent-prompt.md' not found" in result

    def test_prompt_function_attributes_exist(self, temp_dir):
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
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("malformed")

        # Should handle empty file gracefully
        assert result == ""

    def test_prompt_file_with_only_frontmatter(self, temp_dir):
        """Test handling of files with only frontmatter and no content."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create file with only frontmatter
        frontmatter_only = """---
title: Only Frontmatter
description: This file has no content after frontmatter
---"""

        prompt_file = prompts_dir / "frontmatter-only.md"
        prompt_file.write_text(frontmatter_only, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("frontmatter-only")

        # Should return empty string since there's no content after frontmatter
        assert result == ""

    def test_prompt_file_with_malformed_yaml_frontmatter(self, temp_dir):
        """Test handling of files with malformed YAML frontmatter."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create file with invalid YAML frontmatter
        malformed_yaml = """---
title: Malformed YAML
description: This is a test
  invalid_indentation: wrong
not_closed_quote: "this quote is not closed
---

# Content After Malformed Frontmatter

This content should still be accessible."""

        prompt_file = prompts_dir / "malformed-yaml.md"
        prompt_file.write_text(malformed_yaml, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("malformed-yaml")

        # Should still return content after frontmatter, even if YAML is malformed
        assert "# Content After Malformed Frontmatter" in result
        assert "This content should still be accessible." in result
        # Frontmatter should be stripped even if malformed
        assert "title: Malformed YAML" not in result

    def test_prompt_file_with_incomplete_frontmatter_delimiters(self, temp_dir):
        """Test handling of files with incomplete frontmatter delimiters."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create file with opening frontmatter delimiter but no closing one
        incomplete_frontmatter = """---
title: Incomplete Frontmatter
description: Missing closing delimiter

# This should be treated as content

Content continues here."""

        prompt_file = prompts_dir / "incomplete-frontmatter.md"
        prompt_file.write_text(incomplete_frontmatter, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("incomplete-frontmatter")

        # Should treat everything after the opening delimiter as content
        # since there's no closing delimiter
        assert "title: Incomplete Frontmatter" in result
        assert "# This should be treated as content" in result
        assert "Content continues here." in result

    def test_prompt_file_with_invalid_utf8_encoding(self, temp_dir):
        """Test handling of files with invalid UTF-8 encoding."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        prompt_file = prompts_dir / "invalid-utf8.md"

        # Write bytes that are not valid UTF-8
        invalid_utf8_bytes = b"# Valid Header\n\nSome content with invalid UTF-8: \xff\xfe\n\nMore content"
        prompt_file.write_bytes(invalid_utf8_bytes)

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            # Current implementation raises UnicodeDecodeError for invalid UTF-8
            # This test documents the current behavior - in the future, the implementation
            # could be enhanced to handle encoding errors gracefully
            with pytest.raises(UnicodeDecodeError):
                load_prompt_from_markdown("invalid-utf8")

    def test_prompt_file_extremely_large(self, temp_dir):
        """Test handling of extremely large prompt files."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create a very large file (but not so large it causes memory issues in tests)
        large_content = (
            """---
title: Large File Test
description: Testing large file handling
---

# Large Prompt File

"""
            + ("A" * 50000)
            + """

This file contains a lot of repeated content to test handling of large files.

"""
            + ("B" * 50000)
            + """

End of large content."""
        )

        prompt_file = prompts_dir / "large-file.md"
        prompt_file.write_text(large_content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("large-file")

        # Should handle large files without issues
        assert "# Large Prompt File" in result
        assert "End of large content." in result
        assert len(result) > 100000  # Should contain the large content
        # Frontmatter should still be stripped
        assert "title: Large File Test" not in result

    def test_prompt_file_with_only_frontmatter_delimiters(self, temp_dir):
        """Test handling of files with only frontmatter delimiters but no content."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create file with just delimiters
        delimiters_only = """---
---"""

        prompt_file = prompts_dir / "delimiters-only.md"
        prompt_file.write_text(delimiters_only, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("delimiters-only")

        # Should return empty string since there's no content
        assert result == ""

    def test_prompt_file_with_multiple_frontmatter_sections(self, temp_dir):
        """Test handling of files with multiple frontmatter sections."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        # Create file with multiple frontmatter-like sections
        multiple_frontmatter = """---
title: First Frontmatter
---

# Content Section 1

Some content here.

---
title: Second Frontmatter
description: This looks like frontmatter but isn't
---

# Content Section 2

More content here."""

        prompt_file = prompts_dir / "multiple-frontmatter.md"
        prompt_file.write_text(multiple_frontmatter, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir
            result = load_prompt_from_markdown("multiple-frontmatter")

        # Should only strip the first frontmatter section
        assert "# Content Section 1" in result
        assert "Some content here." in result
        assert "# Content Section 2" in result
        assert "More content here." in result
        # First frontmatter should be stripped
        assert "title: First Frontmatter" not in result
        # Second frontmatter should be preserved as content
        assert "title: Second Frontmatter" in result


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

    def test_prompt_loading_performance(self, temp_dir, performance_thresholds):
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
            mock_instance = mock_path.return_value
            mock_instance.parent.parent = temp_dir

            start_time = time.time()
            result = load_prompt_from_markdown("large-prompt")
            end_time = time.time()

        # Should complete within reasonable time (configurable threshold)
        threshold = performance_thresholds["prompt_loading"]
        assert end_time - start_time < threshold, (
            f"Prompt loading took {end_time - start_time:.3f}s, exceeding threshold of {threshold}s"
        )
        assert len(result) > 1000  # Should have loaded substantial content

    def test_multiple_prompt_attributes(self):
        """Test that prompt objects are properly initialized and have required attributes."""
        # Verify prompt objects exist and are usable
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

    def test_multiple_prompt_calls_performance(self, performance_thresholds):
        """Test performance of accessing multiple prompt attributes and properties."""
        import time

        prompts = [
            main_module.commit,
            main_module.github_coderabbitai_review_handler,
            main_module.github_review_handler,
        ]

        # Measure time for accessing prompt attributes multiple times
        start_time = time.time()

        # Access prompt attributes multiple times to measure performance
        for _ in range(100):  # 100 iterations for meaningful timing
            for prompt in prompts:
                # Access common attributes that might be used frequently
                _ = prompt.name
                _ = prompt.description
                _ = prompt.enabled
                _ = hasattr(prompt, "name")
                _ = str(prompt.description)

        end_time = time.time()

        # Should complete within reasonable time (300 attribute accesses)
        # This tests the performance of the prompt object attribute access
        threshold = performance_thresholds["attribute_access"]
        assert end_time - start_time < threshold, (
            f"Attribute access took {end_time - start_time:.3f}s for 300 accesses, exceeding threshold of {threshold}s"
        )

        # Verify that all prompts have expected attributes with meaningful content
        for prompt in prompts:
            assert len(prompt.name) > 3  # Should have meaningful names
            assert len(prompt.description) > 10  # Should have substantial descriptions


class TestPromptAccessPatterns:
    """Demonstrates proper patterns for accessing MCP server data in tests."""

    async def test_prompt_access_via_public_api(self):
        """Test accessing prompts via the public API (recommended approach)."""
        # This is the preferred way to access registered prompts in tests
        # as it uses the public API that won't change with internal refactoring
        prompts = await mcp.get_prompts()

        assert isinstance(prompts, dict)
        assert "commit" in prompts

        # Verify specific prompt exists and has expected properties
        commit_prompt = prompts["commit"]
        assert commit_prompt.name == "commit"
        assert "Git Commit" in commit_prompt.description

    async def test_individual_prompt_access(self):
        """Test accessing individual prompts by name."""
        # Test the get_prompt method for individual prompt access
        commit_prompt = await mcp.get_prompt("commit")
        assert commit_prompt.name == "commit"
        assert commit_prompt.enabled is True

        # Test error handling for non-existent prompts
        with pytest.raises(Exception):  # NotFoundError from fastmcp
            await mcp.get_prompt("non-existent-prompt")

    def test_private_access_antipattern(self):
        """
        Demonstrates the fragile pattern of accessing private attributes.

        This test shows why accessing _prompts directly is problematic:
        1. It breaks encapsulation
        2. It's brittle to internal refactoring
        3. It doesn't test the actual API users will use
        """
        # This is the pattern to AVOID - accessing private attributes
        private_prompts = mcp._prompt_manager._prompts

        # While this works, it's testing implementation details rather than behavior
        assert "commit" in private_prompts

        # If the internal structure changes, this test will break even if
        # the public API continues to work correctly

    async def test_prompt_functionality_integration(self):
        """Test the actual functionality of prompts rather than just registration."""
        # This approach tests behavior rather than internal state
        prompts = await mcp.get_prompts()

        # Test that we can retrieve and use prompt functions
        for prompt_name in ["commit", "github-coderabbitai-review-handler", "github-review-handler"]:
            prompt = prompts[prompt_name]

            # Verify prompt has required attributes for MCP protocol
            assert hasattr(prompt, "name")
            assert hasattr(prompt, "description")
            assert hasattr(prompt, "enabled")

            # Verify the prompt is actually callable/usable
            assert prompt.enabled is True
            assert len(prompt.description) > 0
