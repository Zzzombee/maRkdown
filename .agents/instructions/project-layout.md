# 项目目录合同

本文件是项目目录职责与产物位置的唯一详细规则源。目录清单由 `.agents/config/project-layout.json` 保存；所有新增技能、脚本、模板与文件工作流必须遵守本合同。配置中的 `output_root` 固定为 `outputs`，不得由新功能另设同义输出根目录。

## 固定职责

- 根目录：AGENTS.md、CURRENT_STATE.md、RESEARCH_QUESTIONS.md、PROJECT_STORY.md 与 SOL-###_*.md。稳定编号、block ID 与既有路线不随目录整理改变。
- `.agents/instructions/`：项目规则；`.agents/skills/`：项目技能及其实现/模板；`.agents/config/`：长期配置、来源索引及同步映射。
- `notes/experiments/`：实验分析笔记；`notes/protocols/`：仪器设置和实验流程；`notes/literature/`：文献拆解与项目映射。专题笔记不另建事实权威层。
- `sources/presentations/`：用户提供的原始汇报；`sources/literature/<文献标识>/`：文献主文与补充材料。原始实验数据可保留在项目外，记录真实来源路径，不为套用目录复制整套数据。
- `outputs/reports/<YYYYMMDD_任务>/`：正式汇报、讲稿、作图工作簿及配套说明。
- `outputs/figures/<YYYYMMDD_主题>/`：可交付图片及其必要提示词/生成记录。生成式图片须与实测数据图保留明确来源身份。
- `outputs/deconstruction/<文献标识>/`：逐 panel 对照 PPTX、导出 PDF 与交付说明；拆解笔记正文仍位于 notes/literature/。
- `.planning/<YYYYMMDD_任务>/`：计划、进度、决定及可恢复检查点；已结束任务的日志保留历史语境。
- `.work/<任务>/`：提取、页面渲染、裁图、预览、QA、中间表格与其他临时文件。交付后可保留以便恢复，清理须遵守用户授权。

正式汇报可在包内 `.internal/` 保留精简来源清单、校验结论和 handoff 记录；该目录不存放预览、inspection 日志、中间数据或导出脚本，这些内容仍进入 `.work/` 或相应任务的复现记录。

## 唯一输出根目录

正式产物必须位于 `outputs/`。禁止在项目顶层创建 `output/`、`out/`、`result/`、`results/`、`figures/`、`reports/`、`imagegen/` 及 output/outputs 的拼写变体来承载产物；新增产物类别应在 `outputs/` 下登记子目录。禁止恢复顶层 presentation/、literature_sources/、staging/、tmp/ 或旧分析缓存目录。

配置、技能和命令中的 `--output` 参数名、变量名不受此目录禁令影响。项目外既有数据分析目录中的 output/ 保持其原有身份，不擅自迁移。

工具若不能配置输出路径且自动生成旧目录，立即把本次产物归入上述正式目录或 `.work/`，更新引用，并仅移除本次创建且已空的旧目录；最终交付不得留下并行输出根目录。不要把正式来源、必要复现脚本或唯一副本作为缓存删除。

## 新功能与迁移

创建文件前读取本合同，确定来源、专题笔记、正式产物和中间文件的位置。用户明确要求扩展目录时，先复用既有类别；确需新顶层类别时同步登记目录清单，仍保持 outputs 为唯一产物根目录。任务中间文件不混入项目规则或科研主文件目录。

迁移保留文件名、内容、版本和编号；更新活动笔记链接、来源清单、同步映射及可执行脚本路径。历史快照与 diff 保留原始路径，使用该次迁移清单解释位置变化。目录 junction 指向的共享运行库属于外部依赖，移动链接时不得递归删除或搬动目标。

新增/修改工作流后检查真实目的地；集中完成一次与变更风险匹配的目录、引用及科研结构检查，不用反复全库扫描代替明确的路径规则。
