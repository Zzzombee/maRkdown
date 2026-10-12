import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [input, output, previews] = process.argv.slice(2);
if (!input || !output || !previews) throw new Error('Usage: node export_plot_workbook.mjs data.json output.xlsx preview-directory');
const data = JSON.parse(await fs.readFile(input, 'utf8'));
if ([input, data.source].some(p => path.resolve(p).toLowerCase() === path.resolve(output).toLowerCase())) throw new Error('Refusing to overwrite input');
await fs.mkdir(path.dirname(output), { recursive: true });
await fs.mkdir(previews, { recursive: true });
const wb = Workbook.create();
for (const table of data.tables) {
  const sheet = wb.worksheets.add(table.name);
  const matrix = [table.header, ...table.values];
  const cols = table.header.length;
  const range = sheet.getRangeByIndexes(0, 0, matrix.length, cols);
  range.values = matrix;
  range.format.font = { name: 'Arial', size: 11, color: '#202020' };
  range.format.rowHeight = 21;
  range.format.columnWidth = 25;
  range.format.numberFormat = '0.############';
  const header = sheet.getRangeByIndexes(0, 0, 1, cols);
  header.format.fill = '#E9EEF3';
  header.format.font.bold = true;
  header.format.rowHeight = 27;
  header.format.horizontalAlignment = 'center';
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
}
wb.recalculate();
for (const table of data.tables) {
  const sheet = wb.worksheets.getItem(table.name);
  // Five columns fit the standard preview; independent XY pairs may require a wider view.
  let n = table.header.length, letters = '';
  while (n) { n--; letters = String.fromCharCode(65 + n % 26) + letters; n = Math.floor(n / 26); }
  const view = `A1:${letters}${Math.min(table.values.length + 1, 9)}`;
  const preview = await wb.render({ sheetName: table.name, range: view, scale: 1.4, format: 'png' });
  await fs.writeFile(path.join(previews, `${table.name}.png`), new Uint8Array(await preview.arrayBuffer()));
  const actual = sheet.getRangeByIndexes(0, 0, table.values.length + 1, table.header.length).values;
  if (JSON.stringify(actual) !== JSON.stringify([table.header, ...table.values])) throw new Error(`Value mismatch: ${table.name}`);
}
console.log((await wb.inspect({ kind: 'sheet', include: 'id,name', maxChars: 1000 })).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log(output);
