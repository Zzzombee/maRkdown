# Scholarly source screening policy

This policy governs literature discovered or selected on the user's behalf and any user-designated source that the user explicitly asks to audit against the project gate. Apply source integrity first, claim matching second, and quantitative metrics third.

It does not impose the journal metric gate, citation-age threshold, preferred/restricted classification, exception record, restricted-source warning, or metric audit on an identifiable work that the user explicitly designates by concrete bibliographic citation, stable index such as DOI/PMID/PMCID, or supplied PDF. Handle those works under `SKILL.md` user-designated source mode. In a mixed task, this policy still applies in full to every additional source discovered or selected by Codex. Source authenticity, integrity, and claim matching remain mandatory in both modes.

## 1. Evidence priority

Rank sources by:

1. exact claim and experimental-condition match;
2. study design, reporting quality, and availability of suitable controls;
3. independent replication or convergence;
4. source identity and integrity verification;
5. journal category and Journal Impact Factor;
6. age-adjusted article citation count.

Metrics never upgrade indirect evidence to direct evidence and never convert an author's discussion into an experimental result.

## 2. Absolute exclusion gate

Do not use the following as positive evidence for a project fact, mechanism, safety claim, solution feasibility, or novelty claim:

- retracted or withdrawn articles;
- articles with an unresolved expression of concern or comparably serious integrity warning;
- predatory or hijacked journals, fabricated citations, or sources whose identity cannot be verified;
- sources whose methods or results do not support the cited claim;
- editorials, news releases, marketing materials, peer-review reports, decision letters, corrections standing alone, or supplementary records presented as original experimental evidence;
- preprints or other non-peer-reviewed reports presented as established experimental fact;
- evidence assembled across incompatible materials, cells, species, brain regions, stimulation conditions, or readouts and described as one directly demonstrated mechanism.

Such sources may appear only when the task explicitly discusses research integrity, controversy, provisional emerging evidence, or negative prior art. Label their status and state that they cannot serve as positive evidence. A corrected article may be used only after reading the correction and confirming that the cited result remains valid.

## 3. Default journal metric gate

A peer-reviewed source passes the default journal metric gate when at least one condition is met:

- the journal is JCR Q1 or Q2 in the most relevant subject category for the claim; or
- the latest available Journal Impact Factor is at least 5; or
- the source is an official guideline, consensus, or evidence synthesis issued by a recognized scientific, clinical, governmental, or standards body.

Use the latest available Journal Citation Reports edition for JIF and quartile. Record the JCR edition, the relevant subject category for quartile claims, and the query date. Do not substitute a publisher's promotional metric, an unofficial “impact factor,” CiteScore, SJR, or an inferred value for JCR without explicitly labeling the metric change and treating the source as unverified against this gate.

If neither JCR quartile nor JIF can be verified, classify the source as **restricted — journal metric unverified**. Do not invent or estimate the missing value.

## 4. Age-adjusted article citation alert

Use article-level citations, not a journal's total citations. Prefer one database consistently within a task; use Web of Science or Scopus when available, otherwise OpenAlex or Semantic Scholar. Record the database and query date.

Apply these warning thresholds using time since publication:

| Article age | Citation alert |
|---|---:|
| Less than 2 years | No minimum citation threshold |
| 2–5 years | Fewer than 5 citations |
| More than 5 years | Fewer than 10 citations |

If the count cannot be verified, classify it as **citation count unverified**. A citation alert does not prove poor quality, but it makes the source restricted and triggers the warning requirement. Do not use raw citation counts to compare different fields without noting field and age differences.

## 5. Restricted-source exceptions

A source that fails or cannot be verified against the journal metric or citation-age gate may be retained only when at least one reason applies:

- it is the most direct available match to the project's material-system-stimulation-readout combination;
- it supplies indispensable experimental or methodological detail unavailable from a preferred source;
- it is a field-defining classic, standard method, or original description that cannot be replaced accurately;
- it is too recent to have accumulated citations and is necessary to represent current prior art;
- it belongs to a narrow specialty with systematically lower journal or citation metrics;
- it reports a conflicting, negative, safety, or boundary result necessary to avoid biased synthesis;
- the user explicitly requires that specific source, without asking that its limitations be concealed.

Before retaining it:

1. confirm that no preferred source can support the same claim equally directly;
2. record the exact exception reason;
3. narrow the claim to the experiment actually reported;
4. record whether independent corroboration exists;
5. add the required warning.

Do not use a restricted source as the sole basis for a strong causal, mechanistic, safety, clinical-readiness, or novelty claim. If it is the only evidence available, describe the conclusion as provisional and identify the missing confirmation.

## 6. Required warning

For Obsidian and project Markdown, place this callout at the first substantive use of each restricted source or in a clearly linked source-audit section:

```markdown
> [!warning] 受限来源
> [Author et al., Year](DOI-or-stable-link) 未达到或尚未核验项目默认来源门槛。
> **指标：** JCR 分区 / JIF / 文章被引数；数据源、版本或学科分类及查询日期。
> **保留理由：** 直接模型匹配 / 关键方法 / 经典来源 / 最新研究 / 窄领域 / 冲突或安全证据 / 用户指定。
> **证据边界：** 可支持……；不能支持……。
> **独立佐证：** 有 / 无 / 未核验。
```

For chat or plain-text outputs, use a compact visible form:

```text
⚠ 受限来源：Author et al. (Year)；未达到或未核验的指标：……（来源与日期）；保留理由：……；仅支持：……；不能支持：……；独立佐证：……。
```

For a formal manuscript, proposal, or other artifact where an Obsidian callout would be inappropriate, either replace the restricted source or express the limitation in a footnote, evidence note, or limitations sentence. Also report the restricted-source decision in the handoff. Never silently remove the warning from the overall deliverable.

## 7. Discovery and verification sources

For biomedical topics, discover candidates through PubMed/PMC, OpenAlex, Crossref, and Semantic Scholar. Exclude OpenReview unless the user explicitly requests it.

The global `paper-search` / `paper_search` skill and its `search_papers.py` aggregation script are temporarily disabled for this project. Do not invoke them until the user explicitly re-enables the skill. Discover biomedical literature directly through PubMed/PMC, OpenAlex, Crossref, Semantic Scholar, journal full text, and DOI pages; continue to exclude OpenReview unless the user explicitly requests it.

- Prefer PubMed/PMC, the journal or publisher site, the original full text, or the DOI page for decisive fact verification.
- Use Crossref mainly to discover and verify bibliographic identity and DOI. Filter supplementary material, peer review, decision letters, corrections standing alone, and keyword-only false matches.
- When Semantic Scholar returns HTTP 429, allow one limited retry cycle according to the active search tool. If it still fails, stop that source and continue with the others; do not repeat the same query in the same task.
- Treat database snippets, citation graphs, and automated summaries as discovery aids, not as substitutes for inspecting the underlying paper.

## 8. Claim matching and evidence labels

For each key source, record material, species or experimental system, disease model, brain region or circuit, stimulation method, stimulation timing, readout, and follow-up period.

Use these labels consistently:

- **direct support**: the cited experiment measures the relevant condition and outcome;
- **indirect support**: the experiment differs in a consequential condition but supports part of the reasoning;
- **supports plausibility / is consistent with**: the source makes the mechanism or route conceivable without testing the project claim;
- **conflicting or boundary evidence**: the result limits, contradicts, or conditions the claim;
- **speculation**: a proposed explanation not established by the cited experiment.

Do not state that an indirect or plausibility source “demonstrates” the project claim.

## 9. Citation display

- Apply display-layer links only in user-facing project documents and Codex dialogue. In internal control files, skills, policies, scripts, configuration, provenance records, and temporary work logs, use literal paths, identifiers, DOIs, or URLs instead. Syntax examples and templates that directly specify a user-facing document may retain the target format.
- Use an author-year short link: `[FirstAuthor et al., Year](https://doi.org/...)`; for two authors, `[Author & Author, Year](https://doi.org/...)` is acceptable.
- Link to the DOI when available; otherwise use a stable journal or publisher page.
- Place the citation next to the supported claim.
- Use normal Markdown links for external literature. Use Obsidian wikilinks for project-note and block-ID references only inside Obsidian project notes. In Codex dialogue, use standard Markdown local-file links with absolute paths and forward slashes; wrap targets containing spaces in angle brackets and include line numbers only when verified.
- In project reference lists, keep the author-year link and add one sentence stating the most relevant evidence or boundary.
- Do not repeat full bibliographic records unless the user requests them, identical author-year entries must be disambiguated, or a formal submission bibliography is being prepared.

## 10. Final audit checklist for normal screening mode

- [ ] Every source exists and resolves to the intended work.
- [ ] Retraction, correction, and integrity status were checked for consequential sources.
- [ ] The article's experiment supports the exact cited claim.
- [ ] Material, system, stimulation, readout, and time scale were not silently combined across papers.
- [ ] JCR edition/category and citation database/query date are recorded where metrics are asserted.
- [ ] Every below-threshold or unverified source has an allowed exception and visible warning.
- [ ] Restricted evidence is not the sole support for an unqualified causal, mechanistic, safety, clinical, or novelty claim.
- [ ] Negative-search and novelty statements remain within the recorded search scope.
