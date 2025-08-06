---
skipConfirmation: true
---

# github-coderabbitai-review-handler

**Description:** Finds and processes CodeRabbit AI comments from the current branch's GitHub PR with priority-based handling.

## Instructions

**Step 1: Get CodeRabbit comments using the extraction script**

```bash
# Call the CodeRabbit extraction script with PR info script path
{{SCRIPT_PATHS}}
```

**Step 2: Process the JSON output**

The script returns structured JSON containing:
- `summary`: Counts of actionable, nitpicks, duplicates, outside_diff_range (if any), and total
- `actionable_comments`: Array of HIGH priority issues with AI instructions (body contains direct AI prompts)
  - Each has: priority, title, file, body (body = AI instruction to execute)
- `nitpick_comments`: Array of LOW priority style/maintainability issues with clean descriptions  
  - Each has: priority, title, file, line, body
- `duplicate_comments`: Array of MEDIUM priority duplicates (only present if any exist)
  - Each has: priority, title, file, line, body
- `outside_diff_range_comments`: Array of LOW priority comments on code outside the diff (only present if any exist)
  - Each has: priority, title, file, line, body

**Step 3: PHASE 1 - Collect User Decisions (COLLECTION ONLY - NO PROCESSING)**

**🚨 CRITICAL: This is the COLLECTION phase. Do NOT execute, implement, or process ANY comments yet. Only ask questions and create tasks.**

Go through ALL comments in priority order, collecting user decisions:
1. **HIGH Priority (Actionable)** first
2. **MEDIUM Priority (Duplicates)** - if any exist  
3. **LOW Priority (Nitpicks)** last

**IMPORTANT: Present each comment individually, WAIT for user response, but NEVER execute, implement, or process anything during this phase.**

For actionable comments, present:
```
🤖 AI Instruction (HIGH Priority) - Comment X of Y
📁 File: [file path]
📋 Title: [title]
🎯 Instruction: [body - this is the AI prompt to execute]

Execute this AI instruction? (yes/no/skip)
```

For nitpicks/duplicates, present:
```
🔴 Priority: [MEDIUM/LOW] - Comment X of Y
📁 File: [file path]
📍 Line: [line]
📋 Title: [title]
💬 Description: [body]

Do you want to address this comment? (yes/no/skip)
```

**For each "yes" response:**
- Create a TodoWrite task with appropriate agent assignment
- Show confirmation: "✅ Task created: [brief description]"
- **DO NOT execute the task - Continue to next comment immediately**

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
   - **HIGH Priority (Actionable)**: Execute AI instructions directly using body as prompt
   - **MEDIUM/LOW Priority**: Route to appropriate specialists  
   - Process multiple tasks in parallel when possible
   - Mark each task as completed after finishing

3. **Post-execution workflow:**
   - **Run tests**: Use test-runner agent to run all tests
   - **If tests pass**: Ask user "All tests pass. Do you want to commit the changes? (yes/no)"
   - **If user says yes**: Use git-expert agent to commit changes with descriptive message
   - **If tests fail**: Use debugger agent to analyze and fix test failures, then re-run tests until they pass

**🚨 CRITICAL WORKFLOW:**
- **Phase 1**: ONLY collect decisions (yes/no/skip) and create tasks - NO execution
- **Phase 2**: ONLY execute tasks after ALL comments reviewed - NO more questions
- **Phase 3**: Run tests via test-runner agent, then ask for commit confirmation and use git-expert agent if tests pass

**NEVER mix the phases. Complete each phase fully before starting the next.**
