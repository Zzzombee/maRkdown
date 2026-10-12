# PPTX 生成工作流

## 触发和输入

- 只有用户明确要求创建、生成、补充或同步 PPTX 时才执行。
- 用户只说“以后可以做 PPTX”、“适合 PPTX”或仅要求拆解文档，都不构成授权。
- 必须先有已完成的拆解 Markdown。演示文稿的 panel 范围、顺序、文献解读和项目方案都以该文档为唯一文字来源。
- 若 Markdown 缺少 panel 解读或项目映射，先修复文档，不在 PPTX 中另造一版内容。

## 正式模板

按项目目录合同，正式 PPTX/PDF 放入 `outputs/deconstruction/<paper-key>/`；panel 裁图、图片映射与 QA 放入 `.work/deconstruction/<paper-key>/`。不得采用顶层 output/、staging/ 或 tmp/ 作为默认目的地。

使用 `assets/literature-deconstruction-template.pptx`。该文件是正式视觉原型；`scripts/build_pptx.js` 是其坐标、样式和动态生成逻辑的权威实现。若二者出现差异，以脚本为准重新生成二进制模板，再进行视觉 QA；不得让两个模板长期分叉。模板固定了本线程已确认的视觉结构：

1. 封面页。
2. 使用方式与页码索引页。
3. 主文 panel 原型页。
4. 补充 panel 原型页。

生产演示文稿时，保留封面和导读页；按 Markdown 中的 panel 条目数量复制对应原型页，填充后删除未使用的原型页。可用 `scripts/build_pptx.js` 从结构化 Markdown 和 panel 图片映射文件直接生成同版式产物。

模板文件显示的 `4 slides` 和 `1 / 4`–`4 / 4` 只是四张原型页的占位页数。正式产物必须根据实际 panel 数重算封面总页数和所有页脚页码；生成脚本会自动完成该替换。

## 逐 panel 页面合同

每个单独或允许合并的 panel 占一张幻灯片：

- **左上：** 当页文献 panel 图片，是页面的主要视觉元素。
- **左下：** 来自 Markdown “文献”段的内容、结果和论证作用。
- **右上：** 来自 Markdown “本项目”段的实验、应放图片和叙事作用。
- **右下：** 保持空白数据图占位区，供用户后续填入本项目图片。
- **页脚：** 放稳定的文献引用与页码。

不在右侧加当前证据强弱、完成状态、待填补清单或风险评分。

此处的固定左右对照页面合同是文献拆解产物的任务特定要求，优先于通用 PPTX 指南中“尽量变换布局”的设计偏好。封面与导读页已提供必要的布局变化；panel 页为了快速对照必须保持一致。

## 受限来源在 PPTX 中的警示

若模板文献按 `literature-source-gate` 被保留为受限来源，PPTX 不能只依赖 Markdown 或交接说明中的警示。在封面“证据边界”框内放置精简但可见的证据注释，至少包含：未达到或未核验的指标、保留理由、只能支持的范围、不能支持的范围和独立佐证状态。运行生成脚本时通过 `--boundary` 传入这段警示。

## panel 图片处理

1. 从主文 PDF 和被纳入的补充页面裁取 panel。
2. 裁图要保留完整 panel 标签、坐标、图例、比例尺和直接属于当前 panel 的统计标记。
3. 不带入相邻 panel 标签或与当前标题不一致的定量图。
4. 合并 panel 使用同一张幻灯片，图片排列应保留原论文的阅读顺序。
5. 图片以等比例 contain 方式放入左上框，不拉伸。

## 使用生成脚本

`scripts/build_pptx.js` 提供两种模式：

```text
node scripts/build_pptx.js --template <output.pptx>
node scripts/build_pptx.js --markdown <deconstruction.md> --images <panel-images.json> --output <output.pptx> --citation <footer text> [--boundary <evidence note>]
```

`panel-images.json` 是一个 JSON 对象，key 为 `Figure label|panel label`，value 为 panel 图片绝对路径或相对于 JSON 文件的路径。例如，Markdown 中的 `### Figure 2` 与 `- **c-d**` 使用 key `Figure 2|c-d`。

脚本只读取 Markdown 的“逐 panel 拆解”章节，并要求每个条目同时具有“文献”和“本项目”段。

## QA

沿用本工作流的现有生成脚本；通用 PPTX skill 只补充适用的内容和视觉检查，不要求更换实现库：

1. 文字抽取或 XML 核对：页数、panel 顺序、标题、文献段和本项目段与 Markdown 一致。
2. 全部幻灯片渲染：检查文字溢出、截断、重叠、低对比度和边距。
3. 检查 panel 身份：标题、裁图内标签和 Markdown panel 范围一致。
4. 仅当允许委派且复杂度或风险使独立审查有实质收益时，使用子代理复核。
5. 发现具体问题后修复并复验受影响页面；首轮全部通过即可交付，不为满足循环次数制造修改。
