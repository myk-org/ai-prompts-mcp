"""Utility functions for loading prompts and resolving script paths."""

from pathlib import Path


def get_script_path(script_name: str) -> Path:
    """Get the absolute path to a script in the scripts directory.

    Args:
        script_name: Name of the script (e.g., 'github-coderabbitai-review-handler/get-coderabbit-comments.sh')

    Returns:
        Absolute path to the script
    """
    # Get the parent directory of this utils module (mcp_server)
    mcp_server_dir = Path(__file__).parent.parent
    scripts_dir = mcp_server_dir / "scripts"
    return scripts_dir / script_name


def load_prompt_from_markdown(prompt_name: str, scripts: list[str] | None = None) -> str:
    """Load prompt content from a markdown file in the prompts directory.

    Args:
        prompt_name: Name of the prompt file (without .md extension)
        scripts: List of script paths to replace {{SCRIPT_PATHS}} placeholder.
                Example: ["folder/script1.sh", "folder/script2.sh"]

    Returns:
        The content of the markdown file with metadata stripped and placeholders replaced
    """
    # Get the parent directory of this utils module (mcp_server)
    mcp_server_dir = Path(__file__).parent.parent
    prompts_dir = mcp_server_dir / "prompts"
    prompt_file = prompts_dir / f"{prompt_name}.md"

    if not prompt_file.exists():
        return f"Error: Prompt file '{prompt_name}.md' not found in prompts directory."

    content = prompt_file.read_text(encoding="utf-8")

    # Remove frontmatter if it exists (between --- lines at the start)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    # Replace script placeholders with actual paths
    if scripts:
        # Get full paths for all scripts
        full_paths = [str(get_script_path(script_path)) for script_path in scripts]
        # Join with spaces for command line usage
        script_command = " ".join(full_paths)
        # Replace the placeholder
        content = content.replace("{{SCRIPT_PATHS}}", script_command)

    return content
