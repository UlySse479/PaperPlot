# WORKFLOW.md

## Purpose
Defines the minimal execution flow of the PaperPlot project.

This file answers:
- how tasks are processed
- when each agent is used

It does NOT define:
- agent responsibilities (see AGENTS.md)
- skill policy (see SKILLS.md)

---

## Default Workflow

### 1. Interpret Task
`paperplot-lead` converts user input into a concrete goal.

---

### 2. Classify Task Type
Determine the primary nature of the task:

- system (architecture / abstraction)
- rendering (plot implementation)
- quality (test / validation / docs)
- mixed (cross-boundary)

---

### 3. Delegate (Minimal Principle)
- Use **only one subagent** if possible
- Use multiple only if clearly necessary

---

### 4. Execute
Assigned subagent performs the task within its boundary.

---

### 5. Validate (When Needed)
Use `quality` if the change affects:

- behavior
- visual output
- API
- documentation
- reliability

---

### 6. Integrate
`paperplot-lead` merges outputs into a consistent result.

---

## Cross-Agent Usage

Use multiple agents ONLY when:

- feature spans architecture + implementation
- behavior change requires validation
- rendering affects publication quality

Otherwise: keep single-agent execution.

---

## Completion Rule

A task is complete only if:

- implementation works
- structure is consistent
- output is acceptable for research use
- relevant validation is performed

Code alone is NOT completion.