---
skipConfirmation: false
---

# tasks

**Description:** Task management workflow using Archon MCP server

## Objective

Manage tasks for the current project using the Archon MCP server. This prompt establishes a workflow for project identification, creation, and task management.

## Workflow

### 1. Project Identification

**Goal**: Find or create a project in Archon that corresponds to the current repository.

**Steps**:
1. Determine the current repository name (use git commands)
2. Search for an existing Archon project matching this repository name
3. **Decision Point**:
   - If project exists → Use that `project_id` for task management
   - If project doesn't exist → Create a new Archon project with:
     - Repository name as title
     - Auto-generated description
     - GitHub URL if available

**Note**: Use Archon's project management tools to search and create projects.

### 2. Task Discovery and Assessment

**Goal**: Understand the current task landscape for this project.

**Actions**:
- List all tasks for the project
- Check task statuses (todo, doing, review, done)
- Identify which tasks are currently in progress
- Present a summary to the user

**Note**: Use Archon's task listing and filtering capabilities.

### 3. Task Management Operations

**Goal**: Perform create, update, delete operations based on user needs.

**Common Operations**:
- **Creating tasks**: Add new tasks with clear titles, detailed descriptions, and appropriate assignees
- **Updating tasks**: Change status, reassign, or modify task details
- **Deleting tasks**: Remove obsolete or duplicate tasks
- **Searching tasks**: Find specific tasks by keywords or filters

**Note**: Use Archon's task management tools with appropriate parameters for each operation.

### 4. Task Workflow Best Practices

**Status Flow**: `todo → doing → review → done`

**Critical Rules**:
- Tasks in 'doing' status represent active work
- Tasks in 'review' status are completed but awaiting validation
- Only mark tasks 'done' after verification
- Each task should represent 30 minutes to 4 hours of work

**Parallel Execution**:
- **Multiple independent tasks CAN be worked on simultaneously** when they have no dependencies
- Mark all parallel tasks as 'doing' when starting concurrent work
- Use local TodoWrite for session-level parallel execution tracking
- Use Archon status updates to reflect actual progress on tracked tasks

**Task Granularity**:
- **Feature-specific projects**: Create granular implementation tasks (setup, implement, test, document)
- **Codebase-wide projects**: Create feature-level tasks (major capabilities, integrations)
- Default to more granular when scope is unclear

### 5. Integration Strategy

**Dual-Layer Task Management**:
- **Archon MCP**: Persistent project-level task tracking across sessions
- **Local TodoWrite**: Session-specific granular execution steps and parallel work coordination
- Sync completion status between systems when appropriate

**When to use which**:
- Use Archon for tasks that need persistence and team visibility
- Use local TodoWrite for temporary execution planning within a session
- Use local TodoWrite to track parallel execution of multiple Archon tasks simultaneously

**Parallel Work Pattern**:
1. Mark multiple Archon tasks as 'doing' when starting parallel work
2. Use local TodoWrite to track granular steps for each parallel task
3. Update Archon task status as work completes (doing → review → done)
4. This enables efficient parallel execution while maintaining persistent tracking

## Tool Discovery

You have access to Archon MCP tools through your environment. Use tool discovery to find:
- Project management tools (list, create, update projects)
- Task management tools (list, create, update, delete tasks)
- Document and version management tools (optional advanced features)

Refer to the Archon MCP Server Instructions in your context for complete usage patterns and best practices.

## Expected Behavior

When this prompt is invoked:

1. ✅ Identify current repository
2. ✅ Search for existing Archon project
3. ✅ Create project if needed
4. ✅ Present current tasks (if any)
5. ✅ Ready to manage tasks based on user requests
6. ✅ Follow Archon task management best practices
