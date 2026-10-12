# 空白初始化

仅在用户要求建立空白科研项目框架时使用。简短请求“初始化”须结合科研项目语境与目标目录判断；介绍技能、讨论初始化或初始化程序/仪器均不授权写文件。

## 启动说明与推荐技能

进入初始化执行流程时，先在面向用户的启动消息中明确说明：**强烈建议搭配 Obsidian App 一起使用。** 生成的 Markdown 项目利用 Obsidian 的双向链接、block ID 定位和反向链接组织科研记录；没有安装 Obsidian 也可完成初始化和普通 Markdown 编辑。此提示在启动时给出，不留到最终交付才说明；`--layout-only` 的目录初始化同样适用。

写入前只读检查 `planning-with-files` 和 `obsidian-markdown` 是否可用，不因检查而执行这两个技能的工作流：

- 优先按技能名与路径检查当前会话的可用技能目录，项目内和全局安装均可满足。已有可用入口即通过；同名存在多份时选一个可用入口，不重复加载或执行。
- 技能未出现在会话目录中时，必要时核对目标项目与当前用户实际的技能发现目录及启用状态。使用当前环境解析路径，不硬编码用户名、盘符或另一台机器的技能位置。磁盘存在文件不等于已启用；列表缺项也不直接证明未安装。
- 区分“可用”“已安装但未启用/未被发现”“未找到”和“无法确认”。已安装但不可用时建议检查启用设置或重新打开会话；未找到时建议通过可用的 skill-installer 或已核验的维护仓库安装上游当前发布版本。来源不明时不编造仓库地址、安装命令或版本号。
- 两项均为推荐增强依赖：planning-with-files 支持长期任务恢复，obsidian-markdown 支持 Obsidian 笔记语法。缺少或无法确认时简短说明并继续生成主要文件与目录框架，不将其变为初始化准入条件。

检查结果只在本次会话说明，不写入可移植模板中的本机安装状态。除非用户另行明确要求，不安装、复制、更新或禁用技能，不修改个人配置；不把全局技能副本打包进本项目。初始化检查不自动核验最新版本，安装当前发布版本与后续保持最新分别处理。两项已可用时简短告知即可，不再建议重复安装。

## 目标与已有内容

用户指定目录优先；在明确的新科研项目语境下可使用当前目录。若目标不明确，先只读检查当前目录，缺失信息只阻塞创建，不猜测新位置。遵守目标目录及其父级适用的 AGENTS.md；已有 AGENTS.md 全文读取后保留原有正文与规则，仅在缺少目录合同必读入口时追加该入口，不重写已有章节。若已有规则明确禁止补齐或与目录合同冲突，写入前报告冲突，不静默覆盖。

运行 `scripts/initialize_project.py --check`，检查目标中的三个主要状态文件、SOL 文件以及 Markdown 正文中的稳定编号标题或 block ID。检查不读取科研内容来生成科学判断。发现任一既有状态标记（包括空状态文件、嵌套项目和 SOL）即停止空白初始化，报告具体位置；不覆盖、不自动补齐、不自动切换为维护。只有用户随后明确要求补齐或维护时才进入对应任务。

汇报、原始数据和普通笔记可与空白框架共存；单独存在的 AGENTS.md 也不阻止创建三个状态文件。现有普通笔记若含稳定科研条目，应按已有科研状态处理。扫描排除 `.agents`、`.git`、`.obsidian` 的工具/配置内容，避免把模板当成项目记录。

首次生成目录清单时，脚本自动登记目标中已有的合法顶层目录（例如 data/），原目录与文件保留原位；.git 与 .obsidian 属于环境目录，无需登记。若已有目录清单却出现未登记目录，必须在写入前报告并停止，由明确授权的目录维护先补齐登记；不创建主文件后才报错。禁止的输出别名和旧目录仍要求先迁移，自动登记不豁免它们。

## 复用模板与空白语义

完整读取本技能的 `references/state-schema.md`。脚本复用兄弟技能 `../../pptx-to-research-state/assets/` 中的四个既有模板，不复制一套模板，也不修改 PPTX 初始化流程。缺失必需模板时报告路径并停止创建。

- CURRENT_STATE.md：保留项目目标、实验体系、分析框架、观察、结论、假设、未成立主张、研究方向及近期优先级章节。
- RESEARCH_QUESTIONS.md：保留优先级区域和当前最高优先级问题区域。
- PROJECT_STORY.md：保留文档级目标叙事说明、空的故事框架、固定六节，以及创新定位中的两个子节。
- AGENTS.md：复用通用项目模板，填入用户给出的项目名称/范围；缺少范围时明确待填写。只写实际可用的项目规则路径；没有对应技能时保留模板的手动结构合同和写作底线，不制造强制失效路径。

三个状态文件仅含日期、章节、文档说明和空白提示。移除模板的示例 OBS/CON/HYP/RQ 编号、block ID、示例链接和占位结果；不分配任何稳定编号，不生成科学结论、完整故事正文、文献或 SOL。待填写提示不是科研条目。

## 执行与目录扩展

所有脚本路径以本技能目录为基准。日期显式传入用户时区的当前日期，避免使用执行主机日期。项目名称可采用用户提供的名称或目标目录名；研究范围只使用用户实际给出的文字。

```powershell
python <skill-root>/scripts/initialize_project.py --root <project-root> --date YYYY-MM-DD --check
python <skill-root>/scripts/initialize_project.py --root <project-root> --date YYYY-MM-DD
```

可选参数为 `--project-name`、`--scope` 和可重复的 `--folder`。包含空格的路径和文字须按当前 shell 正确引用。写入前脚本再次检查状态，使用独占创建模式；没有覆盖或强制重置选项。

默认创建四个主要文件（已有 AGENTS.md 时只创建三个），并从 `assets/project-layout.json` 生成标准目录：.agents 的 instructions/skills/config、notes 的 experiments/protocols/literature、sources 的 presentations/literature、outputs 的 reports/figures/deconstruction，以及 .planning 与 .work。同时生成 `.agents/instructions/project-layout.md`、`.agents/config/project-layout.json` 和缺失的 `.gitignore`；已有目录控制文件保留，不复制/安装技能或项目特有学术政策。新生成 AGENTS.md 强制路由到目录合同；已有 AGENTS.md 仅补齐缺失的必读入口。注释、引用块或代码示例中的路径不视为已接入入口。`--check` 明确预告这次追加，重复执行不重复追加。

正式产物唯一根目录为 `outputs/`。脚本拒绝顶层 `output/`、`out/`、`results/` 及旧目录别名；发现既有旧目录时先做明确授权的迁移，不创建第二套目录。用户已指定额外层级时，用 `--folder sources/data/raw --folder outputs/reports/20261012_汇报` 等相对路径增补；新顶层类别须登记，不能绕过唯一输出根目录规则。目录中有 junction 时不跟随到共享依赖。

仅生成框架（例如 PPTX 初始化前、或用户明确要求给已有项目补充目录）时运行以下独立模式。它补充缺失目录与目录控制文件，并为已有 AGENTS.md 补齐缺失的目录必读入口；保留三个科研状态文件、SOL、AGENTS.md 原有规则和已有目录，不绕过普通空白初始化的既有状态检查：

```powershell
python <skill-root>/scripts/initialize_project.py --root <project-root> --date YYYY-MM-DD --layout-only
```

只讨论目录或无目标授权时不得调用该写入模式。后续新增功能必须先读取目标目录合同；工具默认生成旧输出目录时，按合同及时归并。

## 一次验证与完成

创建完成后按 Level 1 对三个新状态文件运行一次 `scripts/validate_state.py --root <project-root> --files CURRENT_STATE.md RESEARCH_QUESTIONS.md PROJECT_STORY.md`；`--layout-only` 未修改科研条目时不跑科研结构校验。运行一次 `scripts/project_layout.py --root <project-root>` 检查目录合同。另检查四主要文件交付、日期、无模板变量/示例条目、AGENTS 规则路径可用及已有文件保留。成功后不重复验证，除非出现新修改或问题。

报告目标目录、实际创建的文件/目录、保留的 AGENTS.md 和校验结果。此流程不初始化调用技能所在的现有项目，除非它确实是用户指定且通过检查的目标。

修改初始化实现后，可运行 `python scripts/test_initialization.py` 做隔离回归验证，覆盖已有目录登记、入口追加、幂等性、旧目录/科研状态保护及失败回滚；普通项目初始化无需重复执行这组实现测试。
