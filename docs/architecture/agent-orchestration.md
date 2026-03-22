# PaperPlot Agent Orchestration Flow

PaperPlot uses a lead-controlled orchestration model.

Only PaperPlot Lead has routing authority.
Subagents do not call each other directly.

## Agents

- PaperPlot Lead: orchestration, task normalization, routing, done criteria, final integration
- System Architect: abstraction governance, token/theme/template/spec/registry/config/override decisions
- Rendering Agent: matplotlib rendering implementation, style mapping, export implementation
- Quality Agent: testing, regression, visual review, docs/examples sync, figure critique

## Canonical Flow

1. Lead normalizes the user request into a structured task
2. Lead determines whether the task involves system-level abstraction or governance
3. If yes, Lead calls System Architect first
4. Lead calls Rendering Agent for implementation when rendering work is needed
5. Lead calls Quality Agent before completion for validation and review
6. Lead integrates all outputs and decides final completion status

## Routing Rules

### Route to System Architect when:
- token/theme/template/spec/registry/config/override is involved
- the correct architectural layer is unclear
- consistency risks or abstraction leakage are likely
- the request may require template registration/versioning or schema changes

### Route to Rendering Agent when:
- rendering behavior is the main task
- renderer/export/style-mapping implementation is needed
- the system layer has already been clarified

### Route to Quality Agent when:
- any code changes
- any rendering or visual output changes
- any export behavior changes
- any docs/examples/README changes
- any template/config changes affecting behavior

## Block Conditions

### System block
If the abstraction layer is wrong or unstable, do not proceed to rendering.

### Rendering block
If rendering would require system-layer hacks, escalate back to Lead.

### Quality block
If tests are missing, regressions are unexplained, visuals degrade, or docs are inconsistent, the task cannot be marked complete.

## Completion Authority

Only PaperPlot Lead can declare a task done.
Subagents provide structured outputs, but not final completion.