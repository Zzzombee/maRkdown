# Research-state schema

Read this file only for structural research-state work routed through `maintain-research-state`.

## File authority and placement

- `CURRENT_STATE.md` stores OBS, CON, and HYP entries and is authoritative for project facts and current interpretations.
- `RESEARCH_QUESTIONS.md` stores RQ entries and their priorities.
- `PROJECT_STORY.md` stores candidate paper narratives and links to project-state entries; it does not create a parallel fact layer.
- Each `SOL-###_*.md` stores one candidate route for one primary RQ. It is a decision artifact, not an experimental-fact authority.

## Stable IDs and blocks

Use these global ID classes:

- `OBS-###`: direct experimental observation;
- `CON-###`: supported conclusion linked to its OBS basis;
- `HYP-###`: working hypothesis linked to the observations or RQ it addresses;
- `RQ-###`: research question;
- `SOL-###`: candidate solution route.

For a new stable entry, use the next number never used in that class. Do not renumber for ordering, reuse a retired number, or assign IDs to ordinary paragraphs, parameters, or todo items.

Keep the Markdown heading and lowercase block ID together. Put the block ID at the end of the first paragraph below the heading, never in the heading:

```markdown
### OBS-001 — Graphene signals at the PC12 membrane region across incubation time

实验观察正文。 ^obs-001
```

Changing a heading title does not change its ID or block ID. Moving an entry requires updating note names in incoming links while preserving the block ID.

## Entry semantics

### OBS

Record the experimental system, known conditions, measurement, time range, comparison, and statistical output that were directly observed. Keep mechanisms, biological meaning, evidence ratings, and phrases such as “证明”“支持”“提示”“意味着” out of the OBS itself.

### CON

Link every conclusion to the OBS entries that support it and state its evidence boundary. Use the following project evidence levels:

- **初步**：qualitative, small-sample, or statistically incomplete evidence requiring important controls or independent repetition;
- **中等**：direct measurement or quantitative comparison with some repetition but a material remaining gap;
- **较强**：multiple consistent direct results, suitable controls, and independent repetition;
- **充分**：a substantially complete evidence chain, statistical hierarchy, decisive controls, and independent replication.

Publication status does not raise the level automatically. Rate separable subclaims independently when their support differs.

### HYP

State the mechanism as unverified and link the OBS or RQ it is intended to explain. Do not promote an HYP to a CON through wording alone.

### RQ

Keep the scientific question and its priority in `RESEARCH_QUESTIONS.md`. If solutions exist, maintain a compact “已形成的解决方案” list linking them without rewriting the RQ to fit a solution.

## User-facing links

Inside Obsidian project notes (`CURRENT_STATE.md`, `RESEARCH_QUESTIONS.md`, `PROJECT_STORY.md`, and SOL notes), render project IDs as Obsidian wikilinks:

```markdown
[[CURRENT_STATE#^obs-001|OBS-001]]
[[CURRENT_STATE#^con-001|CON-001]]
[[CURRENT_STATE#^hyp-001|HYP-001]]
[[RESEARCH_QUESTIONS#^rq-001|RQ-001]]
[[SOL-001_RQ-010_外周神经损伤痛-M1#^sol-001|SOL-001]]
```

In Codex answers to the user, follow `AGENTS.md`: use standard Markdown links with absolute paths and forward slashes, enclosing targets containing spaces in angle brackets. Add line numbers only after verifying them. Use plain or inline-code IDs when no navigation is needed; do not output Obsidian wikilinks in dialogue.

Use standard Markdown links for external literature. Use literal paths, URLs, DOIs, and IDs in control files such as `AGENTS.md`, skill files, scripts, configuration, and working logs. Examples that specify the required user-document syntax may retain wikilinks.

Maintain real relationships rather than decorative links:

- CON links to supporting OBS entries;
- HYP links to what it explains and relevant RQs;
- SOL links to one primary RQ, and that RQ links back to the SOL;
- OBS normally does not contain reverse interpretive links to CON or HYP; use backlinks for reverse navigation.

Each independent reference remains clickable when repeated. Never leave a link pointing to a missing note or block after moving or retiring an entry.

## SOL structure and route protection

Store each solution in a separate filename beginning with its stable ID, preferably `SOL-###_RQ-###_route-name.md`. Require these YAML keys:

```yaml
title:
date:
status:
solution_id:
related_rq:
core_route:
```

Use `# SOL-### — 路线名称` as the main heading. In the first paragraph, identify the primary RQ and summarize the route, ending with `^sol-###`.

Define `core_route` with at least the disease or experimental model, target brain region or circuit, intervention logic, and primary functional objective. Dose exploration, control refinement, implementation versions, and wording changes do not create a new route. A materially different model, target, intervention logic, or functional objective requires a new SOL unless the user explicitly directs replacement of the existing route.

When a route is paused, rejected, or superseded, retain the file, ID, and block ID; update `status` and explain why. Never delete it merely to reuse its number.

## Update order and dates

Preserve contradictory results and unresolved questions. Update a changed durable note's `date` property when the task materially updates its scientific or decision content. A date-only correction does not trigger structural validation.

Apply dependent updates in this order when relevant:

1. `CURRENT_STATE.md`;
2. `RESEARCH_QUESTIONS.md`;
3. affected SOL notes and RQ backlinks;
4. `PROJECT_STORY.md`.

Do not propagate a change into every downstream file automatically. Update only files whose current meaning, feasibility, priority, or narrative is materially affected.
