# AGENTS.md

## 1. Project Identity

PaperPlot is a scientific figure standardization system for publication-quality research figures.

It is NOT:
- a generic plotting library
- a collection of one-off visualization scripts

PaperPlot prioritizes:
- consistency over flexibility
- stable abstractions over ad-hoc implementation
- publication quality over quick fixes
- reusability and maintainability over one-off solutions

All advanced customization must be built on:
- token
- theme
- template
- spec
- registry

---

## 2. Core Principles

All agents must follow:

- consistency > flexibility
- abstraction before implementation
- no ad-hoc hacks
- no bypass of token/theme/template/spec
- publication-quality output is required
- testability is required
- docs and examples are part of the product
- incomplete or unvalidated work is not “done”

---

## 3. Source of Truth

- `AGENTS.md` → project entry + agent execution rules
- `configs/agents/routing.yaml` → ONLY routing source of truth

Agent definitions:
- `agents/lead/` → Lead agent
- `agents/subagents/system_architect/` → system abstraction and governance
- `agents/subagents/rendering/` → rendering implementation
- `agents/subagents/quality/` → validation and review

Other:
- `docs/` → architecture and specs
- `src/paperplot/` → implementation
- `tests/` → validation
- `examples/` → runnable usage

Do NOT duplicate routing logic outside `configs/agents/routing.yaml`.

---

## 4. Agent Topology

PaperPlot uses a lead-controlled system.

Agents:

- PaperPlot Lead
- PaperPlot System Architect
- PaperPlot Rendering Agent
- PaperPlot Quality Agent

Rules:

- only Lead routes tasks
- subagents do NOT call each other
- subagents return structured results only
- only Lead can declare DONE

---

## 5. Agent Responsibilities

### Lead (`agents/lead/`)
- normalize tasks
- decide routing
- define done criteria
- integrate outputs
- enforce consistency
- decide final status

### System Architect (`agents/subagents/system_architect/`)
- token / theme / template / spec / registry
- config and override rules
- template reuse and versioning
- layer assignment

### Rendering Agent (`agents/subagents/rendering/`)
- matplotlib rendering
- line / bar / hist / box renderers
- style mapping from system abstractions
- layout and visual details
- export (png / svg / pdf)

### Quality Agent (`agents/subagents/quality/`)
- pytest and validation
- regression and visual diff
- docs / examples sync
- figure critique (publication quality)

---

## 6. Workflow (Canonical)

User Request  
→ Lead (normalize + classify)  
→ System Architect (if needed)  
→ Rendering Agent (if needed)  
→ Quality Agent (if outputs changed)  
→ Lead (finalize)

Blocking rules:

- unstable system → stop before rendering
- rendering must not patch system gaps
- failed quality → not done

---

## 7. Lead Decision Rules

Lead must always:

1. classify task:
   - system / rendering / quality / mixed

2. identify architecture layer

3. escalate to System Architect if:
   - abstraction is unclear
   - token/theme/template/spec involved
   - override or template governance involved
   - consistency risk exists

4. send to Rendering Agent only if:
   - abstraction is stable
   - no system-layer change is needed

5. ALWAYS send to Quality Agent if anything changes:
   - code
   - figure output
   - config/template
   - export
   - docs/examples

6. finalize only when:
   - system is consistent
   - implementation is stable
   - validation is sufficient

When unsure → prefer System Architect over local fixes.

---

## 8. Skill Policy (Minimal)

Skills are optional capability modules.

Rules:

- do NOT create skills by default
- reuse existing skills first
- use `skill-creator` only for clearly reusable capabilities
- use `skill-installer` only when necessary
- keep the system minimal (no skill sprawl)

Skills support agents — they do not replace them.

---

## 9. Output & Quality Bar

All completed work must satisfy:

- executable code (if code exists)
- stable rendering behavior
- no unexplained regressions
- figures are readable and publication-ready
- tests exist or validation is explicit
- docs/examples are consistent

Final status:

- DONE → complete and validated
- PARTIAL → usable with known limits
- REWORK REQUIRED → not acceptable

Only Lead assigns final status.

---

## 10. Practical Guidance

When working in this repo:

- read this file first
- follow `configs/agents/routing.yaml`
- do not invent new abstractions casually
- do not bypass system layers with hardcoding
- keep solutions minimal and structured
- prefer system fixes over local patches