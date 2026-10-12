---
name: maintain-research-state
description: 从零初始化空白科研项目及标准目录框架（可用“初始化”唤起），或维护 OBS、CON、HYP、RQ、SOL 的编号、链接、元数据和结构。已有科研状态时不执行空白初始化；从汇报提取事实走 PPTX 工作流；只读问答和不改结构的文字编辑不触发。
---

# Maintain Research State

Preserve the project knowledge graph without turning every edit into a repository-wide audit. Apply the smallest validation level justified by the structural risk.

## Select the requested branch

- 用户要求从零创建科研项目框架，或在新科研项目目录中只说“初始化”：读取 [references/initialization.md](references/initialization.md)。启动时先说明强烈建议搭配 Obsidian App 使用，并检查推荐技能的可用性；随后检查目标状态、创建空白框架。不得将“初始化分析/仪器/代码”等其他任务路由到此分支。
- 已有科研状态的编号、链接、元数据或结构维护：使用下方维护流程。用户只说“初始化”而目录已有科研状态时，报告检测结果并停止空白初始化；不要据此自动改写、补齐或重建既有文件。
- 从指定 PPTX 提取事实并建库：使用可用的 `pptx-to-research-state` 初始化或增量分支，不以空白框架代替证据导入。
- 只读问答、纯正文或格式修改：不执行初始化，也不运行结构验证。

保留技能名 `maintain-research-state` 以兼容现有路由；中文入口“科研初始化与维护”和描述中的“初始化”支持简短请求。目标目录不明确时只澄清目标，不在已有项目中猜测另一个输出位置。

## Load only what the operation needs

Read `references/state-schema.md` completely before changing an ID, block ID, cross-note link, entry type, SOL metadata, SOL status, or SOL core route. For a prose-only update that does not change these structures, do not load this reference and do not invoke this skill.

Treat `AGENTS.md` as the authority for scientific evidence boundaries, file responsibilities, literature routing, and writing rules. This skill governs research-state structure and maintenance mechanics; it does not raise evidence strength or decide scientific truth.

创建或迁移项目文件前读取目标的 `.agents/instructions/project-layout.md`。目录清单由 `.agents/config/project-layout.json` 管理；正式产物只进入 `outputs/`。目录初始化和检查复用 `scripts/project_layout.py`，不另建输出根目录。

## Scope the mutation

1. Identify the entries and files that must change by ID, title, and direct links.
2. Read only those entries and the directly affected upstream or downstream entries.
3. Preserve existing IDs and block IDs. Allocate a new ID only for a genuinely new stable entry or route.
4. Before allocating an ID, inventory that ID class once across the controlled project notes and choose the next number never used in a heading, block ID, SOL filename, or retained deprecated entry.
5. Batch related edits before validating. Do not validate after each small patch.

## Apply updates in dependency order

- Record new experimental observations, conclusions, and hypotheses in `CURRENT_STATE.md` first.
- Update `RESEARCH_QUESTIONS.md` only when the evidence changes a question or its priority.
- Update a SOL only when its target decision, feasibility, evidence, or status changes; protect its existing `core_route` unless the user explicitly requests a route change.
- Update `PROJECT_STORY.md` only after its supporting project state or research questions are current.
- When creating a SOL, update the SOL note and its target RQ backlink in the same edit batch.
- When deprecating an entry, retain its ID and block ID and mark its status or replacement. Never recycle the identifier.

## Use a validation budget

Choose one level for the completed edit batch. Do not run a lower level and then repeat it at a higher level unless the first result reveals broader corruption.

### Level 0 — no structural validation

Use for read-only work, prose-only edits, spelling or formatting fixes, citation wording, and date-only metadata changes when IDs, blocks, links, entry types, and SOL route metadata are untouched. Review the edited passage normally; do not run the validator.

### Level 1 — one targeted validation

Use after creating or structurally editing a small number of entries in known files. Run once after all related edits:

```text
python .agents/skills/maintain-research-state/scripts/validate_state.py --root . --files CURRENT_STATE.md RESEARCH_QUESTIONS.md
```

Pass only the files structurally changed. The validator may build a lightweight global ID index to resolve those files, but it reports structural findings for the target scope rather than auditing every note.

### Level 2 — one full audit

Use only when the user explicitly requests a project-wide audit, a refactor moves or retires entries across files, multiple structural changes alter the knowledge graph, concurrent edits may have allocated IDs, or targeted validation indicates wider damage:

```text
python .agents/skills/maintain-research-state/scripts/validate_state.py --root . --full
```

Do not run a full audit merely because a project note was edited. After a successful validation, do not rerun it unless a subsequent change affects the validated structure.

## Handle findings proportionately

- Fix errors introduced by the current task.
- Report unrelated pre-existing errors without silently expanding the task, unless the user requested an audit or the error prevents the requested update.
- Treat warnings as review prompts, not automatic blockers.
- If the script is unavailable, perform the same selected level manually once; do not add extra checks to compensate.

## Finish

Report the files changed, the validation level used, and any unresolved structural issue. Do not narrate every passing check.
