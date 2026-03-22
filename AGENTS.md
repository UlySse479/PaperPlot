## Purpose

This repository uses a minimal multi-agent system to build **PaperPlot**, a research-grade plotting framework.

This file defines ONLY:

* agent organization
* role boundaries
* core project principles

Detailed workflow and skill policies are defined in:

* `.codex/WORKFLOW.md`
* `.codex/SKILLS.md`

---

## Agent Structure

This project uses **1 lead agent + 3 subagents**:

* `paperplot-lead` (controller)
* `system-architect` (structure & abstraction)
* `rendering` (implementation)
* `quality` (validation & consistency)

### Core Rule

* `paperplot-lead` coordinates all work
* subagents do specialized work only
* subagents do NOT redefine global direction

---

## Responsibilities

### `paperplot-lead`

* interpret user intent
* decompose tasks
* assign subagents
* merge results
* ensure consistency

### `system-architect`

* system design
* abstractions (token/theme/template/spec)
* config & extensibility
* long-term structure

### `rendering`

* matplotlib implementation
* plot logic (line/bar/hist/box)
* layout & export
* figure-level details

### `quality`

* testing & regression
* figure quality review
* docs/examples consistency

---

## Design Principles

1. Publication-quality first
2. Consistency over flexibility
3. Minimal abstraction
4. Reuse over reinvention
5. Validation is required (tests/examples)

---

## Boundaries

* Do not expand agent count unless necessary
* Do not move workflow logic into this file
* Do not define skill logic here

This file is the **stable control layer** of the project