# PPTX evidence extraction

Use only for importing evidence from a user-specified PPTX. Resolve `scripts/` and `assets/` below relative to the parent skill directory, and output paths relative to the task work directory. Preserve the source PPTX.

Use the scripts in `scripts/` with the bundled workspace Python runtime. The required environment is:

- Python 3.11 or later;
- `python-pptx` 1.0.2 or a compatible 1.x release;
- Pillow with TIFF support;
- Windows PowerShell and Microsoft PowerPoint desktop for native slide rendering.

MarkItDown, HVE Core, LibreOffice, `uv`, Poppler, and Copilot CLI are not runtime dependencies. The bundled structural extractor includes the two relevant capabilities adapted for this workflow: merged-cell table extraction and native chart category/series/value extraction.

### Preflight and working directory

Read the target project's `.agents/instructions/project-layout.md`. Load the workspace dependency paths, resolve the Python executable, and use `.work/pptx/<input-key>/` as the intermediate work directory; the `work/` paths below denote that directory. Run:

```text
python scripts/preflight.py input.pptx --output work/preflight.json
```

The preflight records file size, slide count, notes, media types, tables, charts, and required environment availability. Reuse prior extraction artifacts only when the source absolute path, size, modification time, and SHA-256 still match.

### Structural extraction

Run:

```text
python scripts/extract_pptx.py input.pptx --output work/structure.json
python scripts/prepare_media_preview.py input.pptx --output-dir work/media
```

`structure.json` preserves slide and shape provenance, recursive group structure, text, notes, table merge geometry, native chart data, and image metadata. `prepare_media_preview.py` preserves each original embedded TIFF by SHA-256 and creates per-frame PNG viewing proxies.

Treat TIFF proxies as display aids. For palette images, preserve the palette when converting; for integer, high-bit-depth, or floating-point images, record the display mapping; for multi-frame TIFFs, retain every frame. Use the original TIFF for pixel values and quantitative analysis.

### Visual extraction

Run:

```text
powershell -File scripts/render_pptx.ps1 -InputPath input.pptx -OutputDir work/slides
python scripts/make_contact_sheet.py work/slides --output-dir work/contact-sheets
```

Inspect every contact sheet, then inspect each evidence-bearing slide at full resolution. Read axes, units, legends, condition labels, sample sizes, statistical marks, representative traces, microscopy panels, and negative results. Use the PowerPoint render as the reference for how TIFFs, crop regions, rotations, overlays, and annotations appear on the slide; use extracted original media when additional pixel-level inspection is needed.

The extraction is complete when both the structural and full-slide visual paths succeed. Do not infer graphical results from slide titles or extracted text alone. Slide conclusions are claims to evaluate, not observations to copy.

### Failure handling

Continue when an optional media proxy or non-evidence-bearing object fails but the structural record, native PowerPoint slide render, and relevant evidence remain available. Record the affected slide, shape, media type, and limitation. Stop before updating research notes when either the structural path or the full-slide visual path is incomplete for evidence-bearing slides.

## 3. Build an evidence ledger

For every evidence-bearing slide, record temporary extraction notes under four headings:

- **Conditions**: sample/system, treatment, controls, timing, dose, stimulus, readout, and analysis level.
- **Direct observations**: visible or reported measurements only.
- **Interpretations/hypotheses**: causal, mechanistic, or biological explanations.
- **Background/story ideas**: motivation, field gap, proposed direction, and literature claims.

Each ledger entry also records source PPTX SHA-256, slide number, panel or shape path, and the supporting structural or visual artifact. Classify numeric readings as:

- **Exact data**: embedded/native chart or source data;
- **Exact label**: a printed value, axis label, or table cell;
- **Visual estimate**: a range or trend estimated from the rendered figure.

Prefer direct graphical or tabular evidence over slide-summary prose when they conflict. Preserve conflicts and missing parameters explicitly. Do not invent sample size, biological replicate count, material specification, stimulation setting, statistical unit, or mechanism.

By default, do not retain file names, slide numbers, or per-slide source fields in the three durable notes. Keep provenance only in temporary working notes unless the user requests it.

## Extraction validation

After the extraction batch, run `python scripts/validate_extraction.py --structure work/structure.json --renders work/slides --media-manifest work/media/manifest.json --output work/validation.json` from the skill directory, substituting the actual work paths. Resolve evidence-bearing failures before writing research notes. This validates extraction only; research-state structure is validated once through maintain-research-state at the end of the edit batch.
