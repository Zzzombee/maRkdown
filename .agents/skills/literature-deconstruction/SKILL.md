---
name: literature-deconstruction
description: 面向用户指定的项目完整论文故事，逐 panel 拆解文献并生成项目图片大纲。普通论文阅读不触发；PPTX 仅在明确要求时生成。
---

# Literature Deconstruction

本 skill 有两个功能：

1. 默认生成逐 panel 文献拆解文档和项目目标图片大纲。
2. 仅在用户明确要求创建、生成或同步 PPTX 时，根据已完成的拆解文档生成逐 panel 对照演示文稿。

仅在请求包含项目故事映射或目标图片大纲时执行此工作流。普通逐图阅读、图注解释或论文总结不进入本 skill 的故事准入；其外部文献仍遵循项目来源门槛。

目标故事线始终由用户指定。用户可以提供文献 PDF、DOI 或正式链接，也可以要求先推荐一篇最匹配文献。

## 必须先执行的准入门槛

在搜索、推荐或开始拆解外部文献之前，完整读取 [references/admission-gate.md](references/admission-gate.md)，并用项目内文档核对用户指定的故事线。

- 准入检查的对象是“完整的目标论文逻辑与试验方案链”，不是当前结果完成度。
- 项目文档是准入与匹配的输入；不要求用户提供原始数据资产。
- 若故事线不完整，立即说明缺少的关键环节并退出。不搜索或推荐文献，不生成拆解文档，不生成 PPTX，也不代替用户补写故事线。
- 若项目内有多条完整故事且用户指向不明，先请用户确定目标，不自行选择。

## 共享边界

- 凡检索、推荐、核验、引用或评价外部文献，先读取并执行项目的 `../literature-source-gate/SKILL.md`。
- 对 PDF 进行逐页视觉核对，不能只依赖摘要、文本抽取或图注。文献为 PDF 时同时执行可用的 PDF skill。
- 拆解文档是目标论文的完整图片蓝图，不是当前证据或数据可用性审计。
- “本项目”部分只说应做的实验、应放的图片和该图在完整故事中的作用；不反复标注“已有基础”“新增实验”“待验证”或“前置阻塞”。
- 可规划未完成实验，但不得把预期结果写成已观察事实。
- 正式拆解正文放入 `notes/literature/`，PPTX/PDF 放入 `outputs/deconstruction/<paper-key>/`，提取、裁图和 QA 中间文件放入 `.work/deconstruction/<paper-key>/`；创建前读取项目目录合同。除非用户另行明确授权，不修改项目状态、研究问题、故事、SOL 或其他核心研究文档。

## 功能一：生成拆解文档

通过准入门槛后，完整读取 [references/document-workflow.md](references/document-workflow.md)，以 [assets/literature-deconstruction-template.md](assets/literature-deconstruction-template.md) 为起点，在 `notes/literature/` 创建并填充本次拆解正文；暂存目录只承载中间文件。

- 用户指定文献时，先核验文献身份、全文和相关补充材料。
- 用户要求推荐时，默认选择一篇与目标故事的论证结构和实验链最匹配的文献；用户要求多篇时才扩展。
- 完成事实提取和结构映射后，必须使用项目的 `../academic-writing-editor/SKILL.md` 做可读性、逻辑和证据边界校订。
- 用户未明确要求 PPTX 时，交付拆解文档后停止。

## 功能二：根据拆解文档生成 PPTX

只有当用户明确要求 PPTX 时才进入此分支。若同一请求同时要求拆解文档和 PPTX，先完成文档，再用它作为演示文稿的唯一文字来源。

完整读取 [references/pptx-workflow.md](references/pptx-workflow.md)，沿用本项目脚本作为生成入口，按可用 PPTX skill 完成适用的内容与视觉检查，并使用 [assets/literature-deconstruction-template.pptx](assets/literature-deconstruction-template.pptx) 作为正式版式模板。如需稳定地重建同一版式，可运行 [scripts/build_pptx.js](scripts/build_pptx.js)。

## 最终验收

- 拆解文档不使用 Markdown 表格。
- 每个 panel 都能让读者快速回答：图中是什么、作者得到什么、它在论文中做什么、本项目做什么。
- 只有相邻 panel 构成同一测量链时才合并；标题直接写 panel 范围，不写“合并”。
- 补充材料只保留与核心对照、机制边界、长期功能或安全直接相关的部分。
- PPTX 的 panel 顺序、文字和合并范围与拆解文档一致，并通过内容和视觉 QA。
