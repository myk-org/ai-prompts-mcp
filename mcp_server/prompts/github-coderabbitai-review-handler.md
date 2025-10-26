---
skipConfirmation: true
---

# github-coderabbitai-review-handler

**Description:** Finds and processes CodeRabbit AI comments from the current branch's GitHub PR with priority-based handling.

---

## 🚨 CRITICAL: SESSION ISOLATION & FLOW ENFORCEMENT

**THIS PROMPT DEFINES A STRICT, SELF-CONTAINED WORKFLOW THAT MUST BE FOLLOWED EXACTLY:**

1. **IGNORE ALL PREVIOUS CONTEXT**: Previous conversations, tasks, or commands in this session are IRRELEVANT
2. **START FRESH**: This prompt creates a NEW workflow that starts from Step 1 and follows the exact sequence below
3. **NO ASSUMPTIONS**: Do NOT assume any steps have been completed - follow the workflow from the beginning
4. **MANDATORY CHECKPOINTS**: Each phase MUST complete fully before proceeding to the next phase
5. **REQUIRED CONFIRMATIONS**: All user confirmations (commit, push) MUST be asked - NEVER skip them

**If this prompt is called multiple times in a session, treat EACH invocation as a completely independent workflow.**

---

## Instructions

**Step 1: Get CodeRabbit comments using the extraction script**

### 🎯 CRITICAL: Simple Command - DO NOT OVERCOMPLICATE

**ALWAYS use this exact command format:**

```bash
{{SCRIPT_PATHS}} <USER_INPUT_IF_PROVIDED>
```

**That's it. Nothing more. No script extraction. No variable assignments. Just one simple command.**

---

**If user provides input (review ID, URL, or commit SHA):**

```bash
# User provided: 3379917343
{{SCRIPT_PATHS}} 3379917343

# User provided: https://github.com/owner/repo/pull/123#pullrequestreview-3379917343
{{SCRIPT_PATHS}} "https://github.com/owner/repo/pull/123#pullrequestreview-3379917343"

# User provided: 6c544434d69b2ef76441949cfe839167b7de775a
{{SCRIPT_PATHS}} 6c544434d69b2ef76441949cfe839167b7de775a
```

**If user provides NO input:**

```bash
# Gets latest commit comments automatically
{{SCRIPT_PATHS}}
```

**THAT'S ALL. DO NOT extract scripts, get PR info, or do ANY bash manipulation. The scripts handle EVERYTHING.**

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

**Step 2.5: Filter Positive Comments from Duplicates**

🎯 **CRITICAL: Before presenting MEDIUM priority comments to user, classify each duplicate comment to filter out positive feedback.**

For each comment in `duplicate_comments` (if any exist), analyze the title and body to determine:

**POSITIVE (Filter Out) - Comments that are:**
- Praise/acknowledgment: Contains words like "good", "great", "nice", "excellent", "perfect", "well done", "correct"
- Positive feedback on fixes: "good fix", "nice improvement", "better approach", "correct implementation"
- Acknowledgment without suggestions: No action words like "should", "consider", "recommend", "suggest", "try"

**ACTIONABLE (Keep) - Comments that:**
- Contain suggestions: "should", "consider", "recommend", "suggest", "could", "might want to"
- Point out issues: "issue", "problem", "concern", "potential", "risk"
- Request changes: "change", "update", "modify", "improve", "refactor"

**Examples:**
- ✅ POSITIVE (filter out): "Windows-safe resource import guard: good portability fix"
- ✅ POSITIVE (filter out): "Nice error handling improvement"
- ❌ ACTIONABLE (keep): "Consider adding error handling here"
- ❌ ACTIONABLE (keep): "This could cause performance issues"

After classification, remove all POSITIVE comments from the `duplicate_comments` array before proceeding to Step 3.

**Step 3: PHASE 1 - Collect User Decisions (COLLECTION ONLY - NO PROCESSING)**

**🚨 CRITICAL: This is the COLLECTION phase. Do NOT execute, implement, or process ANY comments yet. Only ask questions and create tasks.**

Go through ALL comments in priority order, collecting user decisions:
1. **HIGH Priority (Actionable)** first
2. **MEDIUM Priority (Duplicates)** - if any exist  
3. **LOW Priority (Nitpicks and Outside Diff)** last

**IMPORTANT: Present each comment individually, WAIT for user response, but NEVER execute, implement, or process anything during this phase.**

For ALL comment types, use this unified format:
```
🔴 [PRIORITY] Priority - Comment X of Y
📁 File: [file path]
📍 Line: [line] (if available)
📋 Title: [title]
💬 Description: [body]

Do you want to address this comment? (yes/no/skip/all)
```

**For each "yes" response:**
- Create a TodoWrite task with appropriate agent assignment
- Show confirmation: "✅ Task created: [brief description]"
- **DO NOT execute the task - Continue to next comment immediately**

**For "all" response:**
- Create TodoWrite tasks for the current comment AND **ALL remaining comments across ALL priority levels** automatically
- **CRITICAL**: "all" means process EVERY remaining comment (HIGH, MEDIUM, and LOW priority) - do NOT skip any priority level
- Show summary: "✅ Created tasks for current comment + X remaining comments (Y HIGH, Z MEDIUM, W LOW)"
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
   - **🚨 CRITICAL**: Process ALL tasks created during Phase 1, regardless of priority level
   - **NEVER skip LOW priority tasks** - if a task was created in Phase 1, it MUST be executed in Phase 2
   - **HIGH Priority (Actionable)**: Execute AI instructions directly using body as prompt
   - **MEDIUM Priority (Duplicates)**: Route to appropriate specialists using Task tool
   - **LOW Priority (Nitpicks/Outside Diff)**: Route to appropriate specialists using Task tool
   - Process multiple tasks in parallel when possible
   - Mark each task as completed after finishing

3. **Post-execution workflow (PHASES 3 & 4 - MANDATORY CHECKPOINTS):**

   **PHASE 3: Testing & Commit**
   - **STEP 1** (REQUIRED): Use Task tool to run all tests WITH coverage
   - **STEP 2** (REQUIRED): Check BOTH test results AND coverage results:
     - **If tests pass AND coverage passes**: MUST ask: "All tests and coverage pass. Do you want to commit the changes? (yes/no)"
       - If user says "yes": Use Task tool to commit changes with descriptive message
       - If user says "no": Acknowledge and proceed to Phase 4 checkpoint (ask about push anyway)
     - **If tests pass BUT coverage fails**: This is a FAILURE - do NOT ask about commit yet
       - Use Task tool to analyze coverage gaps and add missing tests
       - Re-run tests with coverage until BOTH pass
     - **If tests fail**: Use Task tool to analyze and fix test failures, then re-run until tests pass
   - **CHECKPOINT**: Tests AND coverage BOTH pass, AND commit confirmation asked (even if user declined)

   **PHASE 4: Push to Remote**
   - **STEP 1** (REQUIRED): After successful commit (or commit decline), MUST ask: "Changes committed successfully. Do you want to push the changes to remote? (yes/no)"
     - If no commit was made, ask: "Do you want to push any existing commits to remote? (yes/no)"
   - **STEP 2** (REQUIRED): If user says "yes", use Task tool to push changes to remote
   - **CHECKPOINT**: Push confirmation MUST be asked - this is the final step of the workflow

**🚨 CRITICAL WORKFLOW - STRICT PHASE SEQUENCE:**

This workflow has **4 MANDATORY PHASES** that MUST be executed in order. Each phase has **REQUIRED CHECKPOINTS** that CANNOT be skipped:

**PHASE 1: Collection Phase**
- ONLY collect decisions (yes/no/skip/all) and create tasks - NO execution
- **CHECKPOINT**: ALL comments have been presented and user decisions collected

**PHASE 2: Execution Phase**
- ONLY execute tasks after ALL comments reviewed - NO more questions
- Process ALL approved tasks (HIGH, MEDIUM, LOW priority)
- **CHECKPOINT**: ALL approved tasks have been completed

**PHASE 3: Testing & Commit Phase**
- **MANDATORY STEP 1**: Run tests WITH coverage via Task tool
- **MANDATORY STEP 2**: Check BOTH tests AND coverage - only proceed if BOTH pass
  - If tests pass BUT coverage fails → FIX coverage gaps (this is a FAILURE)
  - If tests fail → FIX test failures
- **MANDATORY STEP 3**: Once BOTH pass, MUST ask user: "All tests and coverage pass. Do you want to commit the changes? (yes/no)"
- **MANDATORY STEP 4**: If user says yes, use Task tool to commit changes
- **CHECKPOINT**: Tests AND coverage BOTH pass, AND commit confirmation asked (even if user declined)

**PHASE 4: Push Phase**
- **MANDATORY STEP 1**: After successful commit, MUST ask user: "Changes committed successfully. Do you want to push the changes to remote? (yes/no)"
- **MANDATORY STEP 2**: If user says yes, use Task tool to push changes
- **CHECKPOINT**: Push confirmation asked (even if user declined)

**🚨 ENFORCEMENT RULES:**
- **NEVER skip phases** - all 4 phases are mandatory
- **NEVER skip checkpoints** - each phase must reach its checkpoint before proceeding
- **NEVER skip confirmations** - commit and push confirmations are REQUIRED even if previously discussed
- **NEVER assume** - always ask for confirmation, never assume user wants to commit/push
- **COMPLETE each phase fully** before starting the next phase

**If tests OR coverage fail**: Use Task tool to analyze and fix failures (add tests for coverage gaps), then re-run tests with coverage until BOTH pass before proceeding to Phase 3's commit confirmation.
