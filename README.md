# maRkdown

**research with markdown** — 基于 **Codex + Obsidian + Python** 的一站式科研进度管理方案。

以 Markdown 保存研究状态，借助 Codex 整理实验进展、维护研究问题和论文故事，通过 Obsidian 的链接组织知识，并用 Python 脚本完成材料提取、数据整理与结构校验。

## 能做什么

- 用 OBS（观察）、CON（结论）、HYP（假设）、RQ（研究问题）和 SOL（解决路线）串联研究进展，区分事实与解释。
- 从实验 PPTX 初始化或增量更新科研记录，保留来源、证据边界、阴性结果与稳定编号。
- 支持文献核验与拆解、学术写作编辑、论文故事整理，以及低精力汇报准备。
- 统一管理规则、技能、模板和脚本，让项目资料与交付产物有固定位置。

## 快速开始

1. 从 [Releases](https://github.com/Zzzombee/maRkdown/releases/latest) 下载 `.agents.zip`，解压到 Obsidian 的科研项目目录；保留 `.agents/` 名称与层级。
2. 在 Codex 中打开同一目录。新项目可要求 Codex“初始化空白科研项目”；也可手动执行：

   ```bash
   python .agents/skills/maintain-research-state/scripts/initialize_project.py --root . --date YYYY-MM-DD --project-name "项目名称" --scope "一句话研究范围"
   ```

   将日期替换为当天日期。初始化生成 `AGENTS.md`、`CURRENT_STATE.md`、`RESEARCH_QUESTIONS.md`、`PROJECT_STORY.md` 与标准目录；已有科研状态时使用增量更新流程。
3. 按需调整 `.agents/config/` 的配置、文献筛选政策、数据入口和汇报偏好，再导入实验资料。日常可直接要求 Codex“整理近期进展”“从这份 PPTX 更新研究状态”或“为指定 RQ 准备方案”。

## 目录与依赖

`.agents/instructions/` 保存项目规则，`config/` 保存配置，`skills/` 包含七项科研技能及其脚本、参考说明和模板。正式产物统一进入 `outputs/`，过程文件进入 `.work/`。

基础环境为 Codex、Obsidian 和 Python 3；按任务安装 `python-pptx`、`Pillow`、`openpyxl`。部分演示与表格脚本还需要 Node.js、`pptxgenjs`、`sharp` 或 Codex 提供的 `@oai/artifact-tool`；PowerPoint 渲染脚本需要 Windows 与 Microsoft PowerPoint。使用前由 Codex 按当前会话定位可用工具与依赖。

本仓库发布规则与工具，不包含原项目实验记录、原始数据或飞书同步配置。本机路径已清理；实验专用映射与偏好保留为可调整示例。学术编辑技能的第三方许可保留在其 `LICENSE` 文件中。
