#!/usr/bin/env python3

import sys

from fastmcp import FastMCP

from mcp_server.utils.utils import load_prompt_from_markdown

mcp = FastMCP("AI Prompts MCP Server")


@mcp.prompt(name="github-coderabbitai-review-handler")
def github_coderabbitai_review_handler() -> str:
    """Process CodeRabbit AI comments from GitHub PR with priority-based handling.

    Finds and processes CodeRabbit AI comments from the current branch's GitHub PR,
    presenting them in priority order for user approval before execution.

    Returns:
        Complete instructions for handling CodeRabbit AI review comments
    """
    scripts = [
        "github-coderabbitai-review-handler/get-coderabbit-comments.sh",
        "general/get-pr-info.sh",
    ]
    return load_prompt_from_markdown("github-coderabbitai-review-handler", scripts)


@mcp.prompt(name="commit")
def commit() -> str:
    """Smart Git Commit with analysis and conventional commit messages.

    Analyzes changes in the git repository and creates meaningful commit messages
    following conventional commit format.

    Returns:
        Complete instructions for smart git commit workflow
    """
    return load_prompt_from_markdown("commit")


@mcp.prompt(name="github-review-handler")
def github_review_handler() -> str:
    """Process human reviewer comments from GitHub PR.

    Finds and processes human reviewer comments from the current branch's GitHub PR,
    extracting feedback and suggestions for implementation.

    Returns:
        Complete instructions for handling human review comments
    """
    scripts = ["github-review-handler/get-human-reviews.sh", "general/get-pr-info.sh"]
    return load_prompt_from_markdown("github-review-handler", scripts)


@mcp.prompt(name="code-review")
def code_review() -> str:
    """Comprehensive code review for security, bugs, performance, and quality issues.

    Analyzes code files for potential security vulnerabilities, common bugs,
    performance concerns, and code quality issues with systematic reporting.

    Returns:
        Complete instructions for conducting thorough code reviews
    """
    return load_prompt_from_markdown("code-review")


@mcp.prompt(name="code-beautifier")
def code_beautifier() -> str:
    """Code beautification and refactoring for improved readability and maintainability.

    Analyzes code structure and formatting to suggest improvements for better
    readability, consistency, and maintainability while preserving functionality.

    Returns:
        Complete instructions for code beautification and refactoring
    """
    return load_prompt_from_markdown("code-beautifier")


@mcp.prompt(name="comment-cleaner")
def comment_cleaner() -> str:
    """Clean up redundant comments while preserving valuable documentation.

    Identifies and removes unnecessary, outdated, or redundant comments while
    maintaining essential documentation and improving code clarity.

    Returns:
        Complete instructions for intelligent comment cleanup
    """
    return load_prompt_from_markdown("comment-cleaner")


@mcp.prompt(name="smart-test-runner")
def smart_test_runner() -> str:
    """Intelligent test running with failure analysis and optimization.

    Provides smart test execution strategies, failure analysis, and optimization
    recommendations for efficient testing workflows and debugging.

    Returns:
        Complete instructions for intelligent test running and analysis
    """
    return load_prompt_from_markdown("smart-test-runner")


@mcp.prompt(name="readme-generator")
def readme_generator() -> str:
    """Analyzes codebase and generates comprehensive, user-friendly README.md.

    Performs thorough codebase analysis to create or refactor README.md files
    with accurate features, installation steps, and usage documentation.

    Returns:
        Complete instructions for generating professional README documentation
    """
    return load_prompt_from_markdown("readme-generator")


def print_available_prompts() -> None:
    """Print all available prompts before server starts."""
    # Get all registered prompts from the prompt manager
    prompt_dict = mcp._prompt_manager._prompts

    if prompt_dict:
        # Sort prompt names for consistent output
        sorted_names = sorted(prompt_dict.keys())

        # Print to stderr so it doesn't interfere with MCP protocol
        print("\n📋 Available Prompts:", file=sys.stderr)
        print("-" * 30, file=sys.stderr)

        for i, name in enumerate(sorted_names, 1):
            prompt_info = prompt_dict[name]
            print(f"  {i}. {name}", file=sys.stderr)
            if hasattr(prompt_info, "description") and prompt_info.description:
                # Take first line of description for brevity
                desc_line = prompt_info.description.split("\n")[0].strip()
                # Note: Even if desc_line is empty (e.g., whitespace-only first line),
                # we still print it with indentation rather than falling back to "No description available"
                print(f"     {desc_line}", file=sys.stderr)
            else:
                print("     No description available", file=sys.stderr)

        print(f"\nTotal: {len(prompt_dict)} prompts registered", file=sys.stderr)
        print("-" * 30, file=sys.stderr)
        print("Server ready for connections...\n", file=sys.stderr)
    else:
        print("No prompts registered", file=sys.stderr)


if __name__ == "__main__":
    print_available_prompts()
    mcp.run()
