# 文件工具路由

用户明确选择的工具、模板和现有专用工作流优先于通用默认。按实际文件操作选择入口，不因讨论“汇报”“slides”或举例提到文件名就启动制作。只读问题只检查必要内容，不编辑或重导出。

创建文件前先读取 `.agents/instructions/project-layout.md`。正式产物统一进入 `outputs/` 对应类别，中间文件进入 `.work/`；工具自动生成的顶层 output/ 等旧目录按合同及时归并，不作为新的长期入口。

## 通用文件

- 新建或编辑普通 PowerPoint：当前 `presentations:Presentations` 插件。
- 新建或编辑普通 XLSX/CSV/TSV：当前 `spreadsheets:Spreadsheets` 插件。活动 Excel 会话另走 `spreadsheets:excel-live-control`。
- PDF 阅读、生成和表单：当前 `pdf:pdf` 插件；Word：`documents:documents`。
- 使用会话技能目录解析当前插件路径，不固定插件缓存版本，不直接修改缓存。
- 全局旧 pptx、xlsx、pdf 的 SKILL.md 已归档到技能扫描目录外，并在配置中保留禁用记录，防止恢复同路径入口后自动启用。其脚本和资源留在原目录；明确选择旧流程时读取该目录的 LEGACY_WORKFLOW.md，而非已归档的 SKILL.md。不要同时加载两套相互冲突的制作配方。若默认插件不可用，说明具体缺口，选择满足请求的可用工具并完成相应检查。

## 现有专用管线

- PPTX 导入科研状态：`pptx-to-research-state` 的结构提取与 PowerPoint 渲染脚本；不改为普通演示文稿创作。
- 项目故事的逐 panel 对照 PPTX：`literature-deconstruction/scripts/build_pptx.js` 和其正式模板。
- Plexon/NeuroExplorer 分析及相关 PPTX：可用时使用当前 NeuroTrain，并按当前会话技能目录定位入口。若入口是 junction，维护在其实际源目录进行。旧电生理备份不可作为当前 Unit/QC 规则来源。
- 已有 HTML 海报转可编辑 PPTX：实际需要该转换时用 html2pptx。
- 低精力汇报：沿用项目 low-energy-research；未明确要求制图或 PPTX 时，只完成其规定的内容、讲稿和数据交付。

这些专用管线现有的 python-pptx、PptxGenJS 等实现是项目认可的具体工具选择；不为满足通用插件的默认实现库重写管线。需要通用文件检查时，只应用与具体工具选择兼容的质量要求。原始数据、科学数值、模板及可编辑性要求始终保留。

## 完成与验证

按实际改动范围完成内容、数值、公式或结构检查；新建/改动版式时做适用的视觉检查。沿用已验证的未变内容，具体问题修复后复验受影响部分。首轮通过即可交付，不强制修改循环、全量重跑或固定数量的子代理。

项目学术写作规则允许必要的被动语态、限定语和技术术语；通用文案偏好不能改变证据表述。用户已有的“不出图、少菜单、少追问”等要求按其作用范围保留。科学图使用真实数据和适合的绘图工具，不用生成式图片替代实验证据。
