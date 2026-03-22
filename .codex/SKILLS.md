# SKILLS.md

## Purpose
Defines when and how skills are used in PaperPlot.

Skills are OPTIONAL helpers, not core structure.

---

## Core Principle

Prefer:
- direct agent execution

Over:
- adding or creating new skills

---

## When to Use Skills

Use a skill ONLY if:

- the capability is clearly reusable
- it reduces duplication or complexity
- it is not already easily handled by agents

---

## Installing Skills

Prefer installing existing high-quality skills:

- use `skill-installer`
- choose well-scoped, relevant skills
- avoid large or generic skill sets

---

## Creating Skills

Use `skill-creator` ONLY if:

- the capability is PaperPlot-specific
- it will be reused multiple times
- it cannot be cleanly handled by agents

---

## Anti-Patterns

Do NOT:

- create skills for one-off tasks
- duplicate agent responsibilities inside skills
- introduce skills that increase system complexity

---

## Minimal Policy

- Fewer skills is better
- Reuse is better than creation
- No skill is better than a bad skill