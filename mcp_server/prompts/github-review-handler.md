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

**Step 3: PHASE 1 - Collect User Decisions (COLLECTION ONLY - NO PROCESSING)**

**🚨 CRITICAL: This is the COLLECTION phase. Do NOT execute, implement, or process ANY comments yet. Only ask questions and create tasks.**

Go through ALL comments sequentially, collecting user decisions:

**IMPORTANT: Present each comment individually, WAIT for user response, but NEVER execute, implement, or process anything during this phase.**

For each comment, present:
```
👤 Human Review - Comment X of Y
👨‍💻 Reviewer: [reviewer name]
📁 File: [file path]
📍 Line: [line]
💬 Comment: [body]

Do you want to address this comment? (yes/no/skip/all)
```

**For each "yes" response:**
- Create a TodoWrite task with appropriate agent assignment
- Show confirmation: "✅ Task created: [brief description]"
- **DO NOT execute the task - Continue to next comment immediately**

**For "all" response:**
- Create TodoWrite tasks for the current comment AND all remaining comments automatically
- Show summary: "✅ Created tasks for current comment + X remaining comments"
- **Skip to Phase 2 immediately**

**For "no" or "skip" responses:**
- Show: "⏭️ Skipped"
- Continue to next comment immediately

**🚨 REMINDER: Do NOT execute, implement, fix, or process anything during this phase. Only collect decisions and create tasks.**

**Step 4: PHASE 2 - Process All Approved Tasks (EXECUTION PHASE)**

**🚨 IMPORTANT: Only start this phase AFTER all comments have been presented and decisions collected.**

After ALL comments have been reviewed in Phase 1:

1. **Show approved tasks and proceed directly:**

```
📋 Processing X approved tasks:
1. [Task description]
2. [Task description]
...
```
Proceed directly to execution (no confirmation needed since user already approved each task in Phase 1)

2. **Process all approved tasks:**
   - Route to appropriate specialists using Task tool based on comment content
   - Process multiple tasks in parallel when possible
   - Mark each task as completed after finishing

3. **Post-execution workflow:**
   - **Run tests**: Use Task tool to select appropriate agent to run all tests
   - **If tests pass**: Ask user "All tests pass. Do you want to commit the changes? (yes/no)"
   - **If user says yes**: Use Task tool to select appropriate agent to commit changes with descriptive message
   - **After successful commit**: Ask user "Changes committed successfully. Do you want to push the changes to remote? (yes/no)"
   - **If user says yes to push**: Use Task tool to select appropriate agent to push changes to remote repository
   - **If tests fail**: Use Task tool to select appropriate agent to analyze and fix test failures, then re-run tests until they pass

**🚨 CRITICAL WORKFLOW:**
- **Phase 1**: ONLY collect decisions (yes/no/skip/all) and create tasks - NO execution
- **Phase 2**: ONLY execute tasks after ALL comments reviewed - NO more questions
- **Phase 3**: Run tests via Task tool, then ask for commit confirmation and use Task tool for git operations if tests pass
- **Phase 4**: After successful commit, ask for push confirmation and use Task tool for git push if approved

**NEVER mix the phases. Complete each phase fully before starting the next.**

Note: Human review comments are treated equally (no priority system like CodeRabbit).
