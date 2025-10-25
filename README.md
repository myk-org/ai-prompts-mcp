# AI Prompts MCP Server

A Model Context Protocol (MCP) server that provides AI prompts using FastMCP. This server loads prompts from markdown files for better maintainability and includes bundled scripts for specific workflows.

## Features

- **GitHub CodeRabbit AI Review Handler**: Process CodeRabbit AI comments from GitHub PRs with priority-based handling
- **GitHub Review Handler**: Process human reviewer comments from GitHub PRs
- **Smart Git Commit**: Analyze changes and create meaningful conventional commit messages

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/myk-org/ai-prompts-mcp
   cd ai-prompts-mcp
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Add to your AI client as an MCP server** (see MCP Configuration section below)

## Running the Server

### Development Mode

```bash
uv run python mcp_server/main.py
```

### MCP Configuration

To use this server with MCP-compatible clients, add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "ai-prompts-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/ai-prompts-mcp",
        "/path/to/ai-prompts-mcp/mcp_server/main.py"
      ]
    }
  }
}
```

Replace `/path/to/ai-prompts-mcp` with the actual path where you cloned this repository.

## Available Prompts

### github_coderabbitai_review_handler

Process CodeRabbit AI comments from GitHub PR with priority-based handling.

Finds and processes CodeRabbit AI comments from the current branch's GitHub PR, presenting them in priority order for user approval before execution.

**Usage:**
- **Default**: Extracts comments from latest commit automatically
- **With parameter**: Provide review ID, review URL, or commit SHA to target specific review
  - Review ID: `3379917343`
  - Review URL: `https://github.com/owner/repo/pull/123#pullrequestreview-3379917343`
  - Commit SHA: `abc1234...`

**Features:**
- Priority-based comment handling (HIGH → MEDIUM → LOW)
- Categorizes comments: actionable, nitpicks, duplicates, outside diff range
- Automatic detection of input type (review ID/URL/commit SHA)

### github_review_handler

Process human reviewer comments from GitHub PR.

Finds and processes human reviewer comments from the current branch's GitHub PR, extracting feedback and suggestions for implementation.

### commit

Smart Git Commit with analysis and conventional commit messages.

Analyzes changes in the git repository and creates meaningful commit messages following conventional commit format.

## Adding New Prompts

1. Create a new markdown file in `mcp_server/prompts/`
2. If the prompt requires scripts, add them to `mcp_server/scripts/[prompt-name]/`
3. Add a new function in `mcp_server/main.py` that uses `load_prompt_from_markdown()`

### Example: Prompt without scripts

```python
@mcp.prompt()
def my_new_prompt() -> str:
    """Description of the new prompt."""
    return load_prompt_from_markdown("my-new-prompt")
```

### Example: Prompt with scripts

1. Create your markdown file with `{{SCRIPT_PATHS}}` placeholder:

````markdown
# My Prompt

Run the following command:

```bash
{{SCRIPT_PATHS}}
```
````

2. Add scripts to `mcp_server/scripts/my-prompt-name/`
3. Create the prompt function:

```python
@mcp.prompt()
def my_new_prompt() -> str:
    """Description of the new prompt."""
    scripts = [
        "my-prompt-name/script1.sh",
        "my-prompt-name/script2.sh"
    ]
    return load_prompt_from_markdown("my-new-prompt", scripts)
```

The `{{SCRIPT_PATHS}}` placeholder will be automatically replaced with the full paths to your scripts.

## Development

This project uses `uv` for dependency management and FastMCP for the MCP server implementation.

The server automatically resolves script paths when prompts are loaded, making it work correctly both in development and when installed as a package.
