---
skipConfirmation: true
---

# github-review-handler

**Description:** Finds and processes human reviewer comments from the current branch's GitHub PR.

## Instructions

**Step 1: Get human review comments using the extraction script**

```bash
# Call the human review extraction script with PR info script path
{{SCRIPT_PATHS}}
```

**Step 2: Process the JSON output**

The script returns structured JSON containing:

- `summary`: Total count of human review comments
- `comments`: Array of review comments from human reviewers
  - Each has: reviewer, file, line, body

**Step 3: Present comments ONE AT A TIME for individual approval**

**IMPORTANT: Present each comment individually and WAIT for user response before showing the next one.**

For each comment, present:

```
👤 Human Review - Comment X of Y
👨‍💻 Reviewer: [reviewer name]
📁 File: [file path]
📍 Line: [line]
💬 Comment: [body]

Do you want to address this comment? (yes/no/skip)
```

**Do NOT present all comments at once. Present one, wait for answer, then proceed to next.**

**Step 4: Process approved comments**

For approved comments:

1. Create todo items with appropriate agent assignment
2. Route to python-expert or appropriate specialist based on comment content
3. Process multiple comments in parallel when possible

Note: Human review comments are treated equally (no priority system like CodeRabbit).
