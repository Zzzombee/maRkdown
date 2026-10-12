---
name: pptx-to-research-state
description: 从用户指定的实验 PPTX 初始化或增量更新科研知识库，创建或维护目标论文故事；也处理用户明确指定 RQ 的 SOL 生成。普通 PPTX 阅读或制作不触发。
---

# PPTX to Research State

Maintain an evidence-bounded project layer: AGENTS.md, CURRENT_STATE.md, RESEARCH_QUESTIONS.md and PROJECT_STORY.md. SOL notes are optional outputs only on an explicit request for a specified RQ. Preserve source PPTX files, user edits, stable IDs, contradictory results and uncertainty.

## Select only the requested branch

- New project from PPTX: [references/initialization.md](references/initialization.md).
- Import results into an existing project: [references/incremental-update.md](references/incremental-update.md), then its extraction reference only if needed.
- Generate or substantively maintain an SOL: [references/solution-workflow.md](references/solution-workflow.md). No PPTX extraction is required for an SOL-only task.
- Create, add or revise a target narrative: [references/story-workflow.md](references/story-workflow.md), using the fixed six-section story template. Add new stories to PROJECT_STORY.md unless the user explicitly requests another destination. Ordinary result imports enter this branch only when a story is affected.
- If the user only asks a question, answer read-only from relevant evidence; do not initialize or update files.

Resolve references relative to this skill. Script and asset paths inside references are relative to this skill's root unless stated otherwise. Do not load every branch in advance.

## Shared contracts

The target project's AGENTS.md governs minimum context, scientific evidence and authorization. Follow its actual routes rather than replacing them with this skill's defaults. In this project, literature-source-gate owns scholarly source policy; maintain-research-state owns structural schema and validation; academic-writing-editor owns the final language pass. Load each only when that aspect of the task applies.

For a target story, the project's story policy owns section responsibilities. Its abstract treats the selected system as a completed, published paper and closes incomplete evidence chains with successful qualitative outcomes, without prospective or conditional wording. Actual evidence and remaining conditions stay in the sixth section; do not fabricate data or promote the narrative to project facts. Apply this distinction during the final academic edit.

For other projects, resolve equivalent existing rules or available skills without creating broken mandatory links or installing dependencies without authorization. If no structure skill exists, the compact AGENTS template supplies a manual fallback. Ordinary academic editing may use the template's evidence-preserving writing rules if no editor exists; explicit SOL generation still requires academic-writing-editor and stops if unavailable. If a project's required literature policy is missing, stop its literature-dependent work; do not invent substitute thresholds.

PPTX evidence requires both structural extraction and visual inspection through the bundled pipeline. Its detailed integrity requirements live in the extraction branch. Mere slide text cannot establish graphical results.

Batch related changes. Validate evidence extraction when used and research-state structure at the single appropriate level; these are different checks, not two full project audits. Complete the selected deliverable and report material unresolved limits concisely.
