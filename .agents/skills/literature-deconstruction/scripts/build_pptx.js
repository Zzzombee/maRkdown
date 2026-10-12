const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const pptxgen = require('pptxgenjs');

const palette = {
  bg: 'F6F5F0',
  ink: '20272B',
  muted: '677176',
  paper: 'FFFFFF',
  graphite: '3F4A4F',
  teal: '2A9D8F',
  tealPale: 'E7F4F1',
  amber: 'E9C46A',
  amberPale: 'FBF4DD',
  line: 'D8DDDA',
  blank: 'FAFBFA',
};

const mainAccents = ['2A9D8F', '3B7EA1', '8F5D9F', 'C06B46', 'A64B59', '667A3E'];

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) throw new Error(`Unexpected argument: ${token}`);
    const key = token.slice(2);
    const value = argv[i + 1];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for --${key}`);
    out[key] = value;
    i += 1;
  }
  return out;
}

function requireFile(filePath, label) {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) throw new Error(`${label} not found: ${resolved}`);
  return resolved;
}

function cleanSlideText(value) {
  return String(value || '')
    .replace(/\[\[[^|\]]+\|([^\]]+)\]\]/g, '$1')
    .replace(/\[\[([^\]#]+)(?:#[^\]]+)?\]\]/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\{\{([^}]+)\}\}/g, '$1');
}

function parseDeconstruction(markdownPath) {
  const lines = fs.readFileSync(markdownPath, 'utf8').split(/\r?\n/);
  const titleLine = lines.find(line => line.startsWith('# '));
  const title = titleLine ? cleanSlideText(titleLine.slice(2).trim()) : path.basename(markdownPath, path.extname(markdownPath));
  const entries = [];
  let section = null;
  let current = null;
  let active = false;

  for (const line of lines) {
    if (line.startsWith('## 2. ')) active = true;
    if (line.startsWith('## 3. ')) break;
    if (!active) continue;

    let match = line.match(/^### (Figure\s+[^｜]+)｜(.+)$/);
    if (match) {
      section = { label: match[1].trim(), title: match[2].trim(), kind: 'main' };
      continue;
    }
    match = line.match(/^#### (Supplementary Figure\s+[^｜]+)｜(.+)$/);
    if (match) {
      section = { label: match[1].trim(), title: match[2].trim(), kind: 'supplement' };
      continue;
    }
    if (!section) continue;

    match = line.match(/^- \*\*(.+?)\*\*$/);
    if (match) {
      current = {
        figureLabel: section.label,
        figureTitle: section.title,
        kind: section.kind,
        panelLabel: match[1].trim(),
        literature: '',
        project: '',
      };
      entries.push(current);
      continue;
    }
    match = line.match(/^  - \*\*文献：\*\* (.+)$/);
    if (match && current) {
      current.literature = match[1].trim();
      continue;
    }
    match = line.match(/^  - \*\*本项目：\*\* (.+)$/);
    if (match && current) current.project = match[1].trim();
  }

  if (!entries.length) throw new Error('No panel entries found in the Markdown section beginning with "## 2.".');
  const incomplete = entries.filter(entry => !entry.literature || !entry.project);
  if (incomplete.length) {
    throw new Error(`Incomplete panel entries: ${incomplete.map(entry => `${entry.figureLabel}|${entry.panelLabel}`).join(', ')}`);
  }
  return { title, entries };
}

function createPresentation() {
  const pptx = new pptxgen();
  pptx.author = 'Codex';
  pptx.subject = 'Panel-by-panel literature deconstruction and project figure mapping';
  pptx.title = 'Literature deconstruction template';
  pptx.lang = 'zh-CN';
  pptx.theme = {
    headFontFace: 'Microsoft YaHei',
    bodyFontFace: 'Microsoft YaHei',
    lang: 'zh-CN',
  };
  pptx.defineLayout({ name: 'DECONSTRUCTION_WIDE', width: 13.333, height: 7.5 });
  pptx.layout = 'DECONSTRUCTION_WIDE';
  return pptx;
}

function makeShadow() {
  return { type: 'outer', color: '000000', blur: 2, offset: 1, angle: 135, opacity: 0.12 };
}

function addTextFit(slide, text, opts) {
  slide.addText(cleanSlideText(text), {
    fontFace: 'Microsoft YaHei',
    margin: 0,
    fit: 'shrink',
    breakLine: false,
    ...opts,
  });
}

async function addContainedImage(slide, imagePath, box) {
  const meta = await sharp(imagePath).metadata();
  if (!meta.width || !meta.height) throw new Error(`Cannot read image dimensions: ${imagePath}`);
  const scale = Math.min(box.w / meta.width, box.h / meta.height);
  const width = meta.width * scale;
  const height = meta.height * scale;
  slide.addImage({
    path: imagePath,
    x: box.x + (box.w - width) / 2,
    y: box.y + (box.h - height) / 2,
    w: width,
    h: height,
    altText: path.basename(imagePath),
  });
}

function addImagePlaceholder(slide, box, accent, label) {
  slide.addShape('roundRect', {
    ...box,
    rectRadius: 0.05,
    line: { color: accent, width: 1.2, dashType: 'dash' },
    fill: { color: palette.blank },
  });
  addTextFit(slide, label, {
    x: box.x + 0.3,
    y: box.y + box.h / 2 - 0.12,
    w: box.w - 0.6,
    h: 0.24,
    fontSize: 13,
    bold: true,
    color: accent,
    align: 'center',
  });
}

function addFooter(slide, citation, slideNum, total, darkBackground = false) {
  const footerColor = darkBackground ? 'AAB4B7' : palette.muted;
  addTextFit(slide, citation, {
    x: 0.45, y: 7.17, w: 9.3, h: 0.17, fontSize: 8.5, color: footerColor,
  });
  addTextFit(slide, `${slideNum} / ${total}`, {
    x: 11.9, y: 7.14, w: 0.95, h: 0.2, fontSize: 9, color: footerColor, align: 'right',
  });
}

function addTitleSlide(pptx, subtitle, boundary, citation, total, dateText) {
  const slide = pptx.addSlide();
  slide.background = { color: palette.ink };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.28, h: 7.5, line: { color: palette.teal, transparency: 100 }, fill: { color: palette.teal } });
  addTextFit(slide, '文献 panel × 本项目目标图片', { x: 0.85, y: 1.12, w: 8.8, h: 0.62, fontSize: 38, bold: true, color: 'FFFFFF' });
  addTextFit(slide, subtitle, { x: 0.88, y: 1.95, w: 8.6, h: 0.5, fontSize: 24, color: palette.amber });
  addTextFit(slide, '左侧：文献内容、结果与作用  ·  右侧：本项目实验与目标图片', { x: 0.9, y: 3.0, w: 9.8, h: 0.36, fontSize: 16, color: 'D8E0DF' });
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.9, y: 4.1, w: 5.55, h: 1.25, rectRadius: 0.06, line: { color: '556066', width: 0.7 }, fill: { color: '2A3338' } });
  addTextFit(slide, '证据边界', { x: 1.18, y: 4.38, w: 1.4, h: 0.25, fontSize: 13, bold: true, color: palette.teal });
  addTextFit(slide, boundary, { x: 1.18, y: 4.75, w: 4.95, h: 0.42, fontSize: 12.5, color: 'FFFFFF' });
  addTextFit(slide, `${total} slides`, { x: 10.3, y: 5.9, w: 2.1, h: 0.5, fontSize: 28, bold: true, color: palette.teal, align: 'right' });
  addTextFit(slide, dateText, { x: 10.35, y: 6.5, w: 2.05, h: 0.25, fontSize: 11, color: 'AAB4B7', align: 'right' });
  addFooter(slide, citation, 1, total, true);
}

function sectionSummary(entries) {
  const sections = [];
  let cursor = 3;
  for (const entry of entries) {
    let section = sections.find(item => item.label === entry.figureLabel);
    if (!section) {
      const mainIndex = sections.filter(item => item.kind === 'main').length;
      section = {
        label: entry.figureLabel,
        title: entry.figureTitle,
        kind: entry.kind,
        accent: entry.kind === 'supplement' ? '6B7280' : mainAccents[mainIndex % mainAccents.length],
        start: cursor,
        end: cursor,
      };
      sections.push(section);
    } else {
      section.end = cursor;
    }
    cursor += 1;
  }
  return sections;
}

function guideSummary(sections) {
  const mainSections = sections.filter(section => section.kind === 'main');
  const supplements = sections.filter(section => section.kind === 'supplement');
  if (!supplements.length) return mainSections;
  const shortLabels = supplements.map(section => {
    const match = section.label.match(/^Supplementary Figure\s+(.+)$/);
    return match ? match[1] : section.label;
  });
  return [
    ...mainSections,
    {
      label: 'Supplement',
      title: shortLabels.join('/'),
      kind: 'supplement',
      accent: '6B7280',
      start: supplements[0].start,
      end: supplements[supplements.length - 1].end,
    },
  ];
}

function addGuideSlide(pptx, sections, citation, total) {
  const slide = pptx.addSlide();
  slide.background = { color: palette.bg };
  addTextFit(slide, '使用方式与页码', { x: 0.55, y: 0.38, w: 5.0, h: 0.5, fontSize: 30, bold: true, color: palette.ink });
  addTextFit(slide, '右下占位框替换为本项目图片；右上说明实验、图片与叙事作用。', { x: 0.58, y: 1.1, w: 7.4, h: 0.44, fontSize: 14, color: palette.muted });

  const maxRows = 7;
  const shown = sections.slice(0, maxRows);
  shown.forEach((item, index) => {
    const y = 1.8 + index * 0.69;
    slide.addShape(pptx.ShapeType.roundRect, { x: 0.6, y, w: 12.1, h: 0.52, rectRadius: 0.06, line: { color: palette.line, width: 0.6 }, fill: { color: palette.paper } });
    slide.addShape(pptx.ShapeType.rect, { x: 0.6, y, w: 0.12, h: 0.52, line: { color: item.accent, transparency: 100 }, fill: { color: item.accent } });
    addTextFit(slide, item.label, { x: 0.95, y: y + 0.16, w: 1.8, h: 0.18, fontSize: 12, bold: true, color: item.accent });
    addTextFit(slide, item.title, { x: 2.9, y: y + 0.15, w: 6.3, h: 0.2, fontSize: 12, color: palette.ink });
    const range = item.start === item.end ? `${item.start}` : `${item.start}-${item.end}`;
    addTextFit(slide, range, { x: 11.1, y: y + 0.15, w: 1.15, h: 0.2, fontSize: 12, bold: true, color: palette.graphite, align: 'right' });
  });
  if (sections.length > maxRows) {
    addTextFit(slide, `另有 ${sections.length - maxRows} 个章节；详见后续页码。`, { x: 9.45, y: 6.72, w: 2.9, h: 0.2, fontSize: 9.5, color: palette.muted, align: 'right' });
  }
  addFooter(slide, citation, 2, total);
}

async function addPanelSlide(pptx, entry, citation, slideNum, total, accent, placeholderMode = false) {
  const slide = pptx.addSlide();
  slide.background = { color: palette.bg };
  const panelTitle = /panel/i.test(entry.panelLabel)
    ? entry.figureLabel
    : `${entry.figureLabel} · panel ${entry.panelLabel}`;
  const supplementMatch = entry.figureLabel.match(/^Supplementary Figure\s+(.+)$/);
  const badgeLabel = placeholderMode
    ? (entry.kind === 'supplement' ? 'SUPP' : 'FIG')
    : (entry.kind === 'supplement' ? (supplementMatch ? supplementMatch[1] : 'SUPP') : entry.figureLabel);

  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.16, line: { color: accent, transparency: 100 }, fill: { color: accent } });
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.45, y: 0.35, w: 1.1, h: 0.35, rectRadius: 0.08, line: { color: accent, transparency: 100 }, fill: { color: accent } });
  addTextFit(slide, badgeLabel, { x: 0.56, y: 0.42, w: 0.88, h: 0.18, fontSize: 10.5, bold: true, color: 'FFFFFF', align: 'center' });
  addTextFit(slide, panelTitle, { x: 1.75, y: 0.28, w: 6.3, h: 0.37, fontSize: entry.kind === 'supplement' ? 20 : 24, bold: true, color: palette.ink });
  addTextFit(slide, entry.figureTitle, { x: 8.1, y: 0.36, w: 4.75, h: 0.28, fontSize: 12.5, color: accent, align: 'right' });

  addTextFit(slide, '文献 panel', { x: 0.47, y: 0.86, w: 2.0, h: 0.25, fontSize: 13, bold: true, color: palette.graphite });
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.45, y: 1.13, w: 6.7, h: 3.68, rectRadius: 0.06, line: { color: 'D7DBD8', width: 0.7 }, fill: { color: palette.paper }, shadow: makeShadow() });
  if (placeholderMode) {
    addImagePlaceholder(slide, { x: 0.62, y: 1.28, w: 6.36, h: 3.38 }, accent, '文献 panel 图片');
  } else {
    await addContainedImage(slide, entry.image, { x: 0.62, y: 1.28, w: 6.36, h: 3.38 });
  }

  slide.addShape(pptx.ShapeType.roundRect, { x: 0.45, y: 5.02, w: 6.7, h: 1.92, rectRadius: 0.06, line: { color: 'D7DBD8', width: 0.7 }, fill: { color: palette.paper } });
  addTextFit(slide, '文献解读', { x: 0.67, y: 5.2, w: 1.2, h: 0.24, fontSize: 12.5, bold: true, color: accent });
  addTextFit(slide, entry.literature, { x: 0.67, y: 5.53, w: 6.24, h: 1.13, fontSize: 11.6, color: palette.ink, valign: 'top', breakLine: true });

  slide.addShape(pptx.ShapeType.line, { x: 7.47, y: 0.92, w: 0, h: 6.02, line: { color: 'D1D6D3', width: 1 } });
  addTextFit(slide, '本项目方案', { x: 7.78, y: 0.86, w: 2.0, h: 0.25, fontSize: 13, bold: true, color: palette.graphite });
  slide.addShape(pptx.ShapeType.roundRect, { x: 7.74, y: 1.13, w: 5.12, h: 1.72, rectRadius: 0.06, line: { color: accent, width: 0.8 }, fill: { color: entry.kind === 'supplement' ? palette.amberPale : palette.tealPale } });
  addTextFit(slide, entry.project, { x: 7.98, y: 1.36, w: 4.65, h: 1.24, fontSize: 11.3, color: palette.ink, valign: 'top', breakLine: true });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.74, y: 3.08, w: 5.12, h: 3.86, rectRadius: 0.06,
    line: { color: accent, width: 1.5, dashType: 'dash' }, fill: { color: palette.blank },
  });
  slide.addShape(pptx.ShapeType.roundRect, { x: 9.48, y: 4.24, w: 1.65, h: 0.58, rectRadius: 0.08, line: { color: accent, width: 0.8 }, fill: { color: palette.paper } });
  addTextFit(slide, '粘贴项目数据图', { x: 9.62, y: 4.43, w: 1.38, h: 0.18, fontSize: 11, bold: true, color: accent, align: 'center' });
  addTextFit(slide, '建议保留原始 panel 标签、样本量与统计单位', { x: 8.42, y: 5.05, w: 3.8, h: 0.24, fontSize: 9.5, color: palette.muted, align: 'center' });
  addFooter(slide, citation, slideNum, total);
}

async function buildTemplate(outputPath) {
  const pptx = createPresentation();
  const citation = '〔文献引用〕';
  const total = 4;
  addTitleSlide(pptx, '〔文献简称〕拆解对照', '填写文献事实与项目目标设计之间的证据边界。', citation, total, '〔日期〕');
  const sections = [
    { label: 'Figure X', title: '图级论证作用', kind: 'main', accent: mainAccents[0], start: 3, end: 3 },
    { label: 'Supplementary Figure Sx', title: '纳入理由', kind: 'supplement', accent: '6B7280', start: 4, end: 4 },
  ];
  addGuideSlide(pptx, guideSummary(sections), citation, total);
  await addPanelSlide(pptx, {
    figureLabel: 'Figure X', figureTitle: '图级论证作用', kind: 'main', panelLabel: 'a',
    literature: '填写该 panel 的内容、直接结果与论证作用。', project: '填写本项目的实验、目标图片与叙事作用。',
  }, citation, 3, total, mainAccents[0], true);
  await addPanelSlide(pptx, {
    figureLabel: 'Supplementary Figure Sx', figureTitle: '纳入理由', kind: 'supplement', panelLabel: 'a-b',
    literature: '填写该 panel 的内容、直接结果与论证作用。', project: '填写本项目的实验、目标图片与叙事作用。',
  }, citation, 4, total, '6B7280', true);
  await pptx.writeFile({ fileName: path.resolve(outputPath) });
}

async function buildFromMarkdown(args) {
  const markdownPath = requireFile(args.markdown, 'Markdown');
  const imagesPath = requireFile(args.images, 'Panel image manifest');
  const outputPath = path.resolve(args.output);
  if (!args.citation) throw new Error('--citation is required when generating a production deck.');

  const parsed = parseDeconstruction(markdownPath);
  const imageMap = JSON.parse(fs.readFileSync(imagesPath, 'utf8'));
  const imageBase = path.dirname(imagesPath);
  for (const entry of parsed.entries) {
    const key = `${entry.figureLabel}|${entry.panelLabel}`;
    if (!Object.prototype.hasOwnProperty.call(imageMap, key)) throw new Error(`Missing panel image mapping: ${key}`);
    const candidate = path.isAbsolute(imageMap[key]) ? imageMap[key] : path.resolve(imageBase, imageMap[key]);
    entry.image = requireFile(candidate, `Panel image for ${key}`);
  }

  const sections = sectionSummary(parsed.entries);
  const accentBySection = new Map(sections.map(section => [section.label, section.accent]));
  const total = parsed.entries.length + 2;
  const pptx = createPresentation();
  const boundaryText = args.boundary || '文献结果用于论证结构与实验设计参照；本项目区域描述目标实验和图片，不把计划写成既有结果。';
  addTitleSlide(
    pptx,
    parsed.title,
    boundaryText,
    args.citation,
    total,
    new Date().toISOString().slice(0, 10),
  );
  addGuideSlide(pptx, guideSummary(sections), args.citation, total);
  for (let index = 0; index < parsed.entries.length; index += 1) {
    const entry = parsed.entries[index];
    await addPanelSlide(pptx, entry, args.citation, index + 3, total, accentBySection.get(entry.figureLabel));
  }
  await pptx.writeFile({ fileName: outputPath });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.template) {
    await buildTemplate(args.template);
    process.stdout.write(`Wrote template: ${path.resolve(args.template)}\n`);
    return;
  }
  if (args['validate-markdown']) {
    const markdownPath = requireFile(args['validate-markdown'], 'Markdown');
    const parsed = parseDeconstruction(markdownPath);
    process.stdout.write(`Valid Markdown: ${parsed.entries.length} panel entries across ${sectionSummary(parsed.entries).length} sections.\n`);
    return;
  }
  if (!args.markdown || !args.images || !args.output) {
    throw new Error('Use --template <output.pptx>, --validate-markdown <file.md>, or --markdown <file.md> --images <panel-images.json> --output <file.pptx> --citation <text> [--boundary <text>].');
  }
  await buildFromMarkdown(args);
  process.stdout.write(`Wrote deck: ${path.resolve(args.output)}\n`);
}

main().catch(error => {
  process.stderr.write(`${error.stack || error.message}\n`);
  process.exitCode = 1;
});
