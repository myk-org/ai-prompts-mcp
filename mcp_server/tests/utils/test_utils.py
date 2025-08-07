"""Tests for mcp_server.utils.utils module."""

from pathlib import Path
from unittest.mock import patch

from mcp_server.utils.utils import get_script_path, load_prompt_from_markdown


class TestGetScriptPath:
    """Test cases for get_script_path function."""

    def test_get_script_path_basic(self):
        """Test basic script path resolution."""
        script_name = "test-folder/test-script.sh"
        result = get_script_path(script_name)

        # Should return a Path object
        assert isinstance(result, Path)

        # Should end with the script name
        assert str(result).endswith("scripts/test-folder/test-script.sh")

        # Should be absolute
        assert result.is_absolute()

    def test_get_script_path_with_subdirectories(self):
        """Test script path resolution with multiple subdirectories."""
        script_name = "github-coderabbitai-review-handler/get-coderabbit-comments.sh"
        result = get_script_path(script_name)

        assert isinstance(result, Path)
        assert str(result).endswith("scripts/github-coderabbitai-review-handler/get-coderabbit-comments.sh")
        assert result.is_absolute()

    def test_get_script_path_simple_filename(self):
        """Test script path resolution with just a filename."""
        script_name = "simple-script.sh"
        result = get_script_path(script_name)

        assert isinstance(result, Path)
        assert str(result).endswith("scripts/simple-script.sh")
        assert result.is_absolute()

    def test_get_script_path_empty_string(self):
        """Test script path resolution with empty string.

        Edge case: When script_name is empty, the function returns the base scripts
        directory path. This behavior occurs because PathLib's / operator with an
        empty string simply returns the left operand (scripts_dir / "" == scripts_dir).
        """
        script_name = ""
        result = get_script_path(script_name)

        assert isinstance(result, Path)
        # When script_name is empty, should return the scripts directory itself
        assert str(result).endswith("scripts")
        # More specific assertion: the path should end exactly with "mcp_server/scripts"
        # and not contain any additional path components after "scripts"
        assert str(result).endswith("mcp_server/scripts")
        # Verify no trailing separators or additional components
        assert result.name == "scripts"

    def test_get_script_path_relative_to_utils_module(self):
        """Test that script path is correctly resolved relative to utils module."""
        script_name = "test.sh"
        result = get_script_path(script_name)

        # The path should contain mcp_server/scripts
        assert "mcp_server/scripts" in str(result)


class TestLoadPromptFromMarkdown:
    """Test cases for load_prompt_from_markdown function."""

    def test_load_prompt_from_markdown_file_not_found(self, temp_dir):
        """Test behavior when prompt file doesn't exist."""
        # Create prompts directory but not the file we're looking for
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("nonexistent")

        assert "Error: Prompt file 'nonexistent.md' not found in prompts directory." in result

    def test_load_prompt_from_markdown_with_frontmatter(self, temp_dir):
        """Test loading markdown with frontmatter."""
        # Create test file structure
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """---
title: Test Prompt
description: A test prompt
---

# Test Prompt

This is a test prompt content."""

        prompt_file.write_text(content, encoding="utf-8")

        # Mock the module path resolution
        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt")

        # Should strip frontmatter
        assert "---" not in result
        assert "title: Test Prompt" not in result
        assert "# Test Prompt" in result
        assert "This is a test prompt content." in result

    def test_load_prompt_from_markdown_without_frontmatter(self, temp_dir):
        """Test loading markdown without frontmatter."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """# Test Prompt

This is a test prompt content without frontmatter."""

        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt")

        assert "# Test Prompt" in result
        assert "This is a test prompt content without frontmatter." in result

    def test_load_prompt_from_markdown_with_script_replacement(self, temp_dir):
        """Test script placeholder replacement functionality."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """# Test Prompt

Execute: {{SCRIPT_PATHS}}

Additional content."""

        prompt_file.write_text(content, encoding="utf-8")

        scripts = ["folder/script1.sh", "folder/script2.sh"]

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            with patch("mcp_server.utils.utils.get_script_path") as mock_get_script:
                mock_get_script.side_effect = [
                    Path("/test/scripts/folder/script1.sh"),
                    Path("/test/scripts/folder/script2.sh"),
                ]
                result = load_prompt_from_markdown("test-prompt", scripts)

        assert "{{SCRIPT_PATHS}}" not in result
        assert "/test/scripts/folder/script1.sh /test/scripts/folder/script2.sh" in result

    def test_load_prompt_from_markdown_no_script_replacement(self, temp_dir):
        """Test that placeholders remain when no scripts provided."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """# Test Prompt

Execute: {{SCRIPT_PATHS}}

Additional content."""

        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt")

        # Placeholder should remain when no scripts provided
        assert "{{SCRIPT_PATHS}}" in result

    def test_load_prompt_from_markdown_empty_scripts_list(self, temp_dir):
        """Test behavior with empty scripts list."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """# Test Prompt

Execute: {{SCRIPT_PATHS}}"""

        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt", [])

        # Empty scripts list is falsy, so placeholder replacement is skipped
        assert "{{SCRIPT_PATHS}}" in result

    def test_load_prompt_from_markdown_malformed_frontmatter(self, temp_dir):
        """Test handling of malformed frontmatter."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """---
title: Test Prompt
# malformed yaml
---

# Test Prompt

Content here."""

        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt")

        # Should still strip frontmatter even if malformed
        assert "title: Test Prompt" not in result
        assert "# Test Prompt" in result
        assert "Content here." in result

    def test_load_prompt_from_markdown_only_frontmatter(self, temp_dir):
        """Test file with only frontmatter."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """---
title: Test Prompt
description: A test prompt
---"""

        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt")

        # Should return empty string after stripping frontmatter
        assert result.strip() == ""

    def test_load_prompt_from_markdown_incomplete_frontmatter(self, temp_dir):
        """Test file with incomplete frontmatter (only opening ---)."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """---
title: Test Prompt
This has only one --- at the start

# Test Prompt

Content here."""

        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt")

        # When splitting on "---" with maxsplit=2, we get:
        # parts[0] = "" (before first ---)
        # parts[1] = "\ntitle: Test Prompt\nThis has only one "
        # parts[2] = " at the start\n\n# Test Prompt\n\nContent here."
        # Since len(parts) >= 3, it strips frontmatter and returns parts[2].strip()

        # Verify the function correctly identifies this as having frontmatter
        # and returns the content after the first "---" occurrence
        assert "# Test Prompt" in result
        assert "Content here." in result

        # Verify frontmatter content is stripped
        assert "title: Test Prompt" not in result

        # Verify specific behavior: the content starts with "at the start"
        # (the remainder after the split on the partial "---" in the content)
        # Note: the leading space is stripped by the function
        assert result.startswith("at the start")

        # Verify the result contains the expected structure
        expected_parts = ["at the start", "# Test Prompt", "Content here."]
        for part in expected_parts:
            assert part in result

    def test_load_prompt_from_markdown_utf8_encoding(self, temp_dir):
        """Test proper UTF-8 encoding handling."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """# Test Prompt

Unicode content: 🚀 émojis and ñ characters."""

        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            result = load_prompt_from_markdown("test-prompt")

        assert "🚀 émojis and ñ characters" in result

    def test_load_prompt_from_markdown_single_script(self, temp_dir):
        """Test script replacement with single script."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        prompt_file = prompts_dir / "test-prompt.md"

        content = """Run: {{SCRIPT_PATHS}}"""
        prompt_file.write_text(content, encoding="utf-8")

        with patch("mcp_server.utils.utils.Path") as mock_path:
            mock_path.return_value.parent.parent = temp_dir
            with patch("mcp_server.utils.utils.get_script_path") as mock_get_script:
                mock_get_script.return_value = Path("/test/scripts/single.sh")
                result = load_prompt_from_markdown("test-prompt", ["single.sh"])

        assert "{{SCRIPT_PATHS}}" not in result
        assert "/test/scripts/single.sh" in result
