#!/usr/bin/env python3
"""Proportionate structural validation for project research-state Markdown."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ID_TYPES = "OBS|CON|HYP|RQ|SOL"
HEADING_RE = re.compile(rf"^#{{1,6}}\s+((?:{ID_TYPES})-\d{{3}})\b", re.MULTILINE)
BLOCK_RE = re.compile(rf"(?<![#\w])\^((?:{ID_TYPES.lower()})-\d{{3}})\b", re.IGNORECASE)
LINK_RE = re.compile(
    rf"\[\[(?P<note>[^#|\]]*)#\^(?P<block>(?:{ID_TYPES.lower()})-\d{{3}})(?:\|(?P<label>[^\]]+))?\]\]",
    re.IGNORECASE,
)
SOL_NAME_RE = re.compile(r"^(SOL-\d{3})_.*\.md$", re.IGNORECASE)
FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(?P<body>.*?)\r?\n---\s*\r?\n", re.DOTALL)
YAML_KEY_RE = re.compile(r"^(?P<key>[A-Za-z_][\w-]*):\s*(?P<value>.*)$", re.MULTILINE)
REQUIRED_SOL_KEYS = {"title", "date", "status", "solution_id", "related_rq", "core_route"}


@dataclass(frozen=True)
class Finding:
    level: str
    path: Path
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def controlled_files(root: Path) -> list[Path]:
    files = []
    for name in ("CURRENT_STATE.md", "RESEARCH_QUESTIONS.md", "PROJECT_STORY.md"):
        path = root / name
        if path.is_file():
            files.append(path.resolve())
    files.extend(path.resolve() for path in root.glob("SOL-*.md") if path.is_file())
    return sorted(set(files), key=lambda p: str(p).lower())


def resolve_targets(root: Path, names: list[str], known: list[Path]) -> list[Path]:
    known_set = set(known)
    targets = []
    for name in names:
        path = Path(name)
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        if not path.is_file():
            raise ValueError(f"target file does not exist: {path}")
        if path not in known_set:
            raise ValueError(f"target is outside controlled research-state notes: {path}")
        targets.append(path)
    return sorted(set(targets), key=lambda p: str(p).lower())


def note_index(paths: list[Path]) -> dict[str, Path]:
    return {path.stem.casefold(): path for path in paths}


def section_has_expected_block(text: str, heading: re.Match[str]) -> bool:
    line_end = text.find("\n", heading.start())
    if line_end == -1:
        line_end = len(text)
    marker = text[heading.start() : line_end]
    level = len(marker) - len(marker.lstrip("#"))
    next_heading = re.search(rf"^#{{1,{level}}}\s+", text[heading.end() :], re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading else len(text)
    expected = "^" + heading.group(1).lower()
    return re.search(rf"(?<![#\w]){re.escape(expected)}\b", text[heading.end() : end], re.IGNORECASE) is not None


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}
    return {
        item.group("key"): item.group("value").strip().strip("\"'")
        for item in YAML_KEY_RE.finditer(match.group("body"))
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate named research-state files by default; use --full explicitly for a project-wide audit."
    )
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--files", nargs="+", help="Structurally changed files to validate once")
    scope.add_argument("--full", action="store_true", help="Explicitly audit all controlled research-state notes")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    known = controlled_files(root)
    if not known:
        parser.error(f"no controlled research-state notes found under {root}")
    try:
        targets = known if args.full else resolve_targets(root, args.files, known)
    except ValueError as exc:
        parser.error(str(exc))

    texts = {path: read_text(path) for path in known}
    target_set = set(targets)
    findings: list[Finding] = []

    headings: dict[str, list[Path]] = defaultdict(list)
    blocks: dict[str, list[Path]] = defaultdict(list)
    for path, text in texts.items():
        for match in HEADING_RE.finditer(text):
            headings[match.group(1).upper()].append(path)
        for match in BLOCK_RE.finditer(text):
            blocks[match.group(1).upper()].append(path)

    for identifier, paths in headings.items():
        if len(paths) > 1 and (args.full or target_set.intersection(paths)):
            locations = ", ".join(str(path.relative_to(root)) for path in paths)
            findings.append(Finding("ERROR", paths[0], f"duplicate heading {identifier}: {locations}"))
    for identifier, paths in blocks.items():
        if len(paths) > 1 and (args.full or target_set.intersection(paths)):
            locations = ", ".join(str(path.relative_to(root)) for path in paths)
            findings.append(Finding("ERROR", paths[0], f"duplicate block ^{identifier.lower()}: {locations}"))

    notes = note_index(known)
    for path in targets:
        text = texts[path]
        file_headings = list(HEADING_RE.finditer(text))
        for heading in file_headings:
            identifier = heading.group(1).upper()
            if not section_has_expected_block(text, heading):
                findings.append(Finding("ERROR", path, f"{identifier} lacks ^{identifier.lower()} in its section"))

        for link in LINK_RE.finditer(text):
            note_name = Path(link.group("note")).name.casefold() if link.group("note") else path.stem.casefold()
            target = notes.get(note_name)
            block = link.group("block").upper()
            if target is None:
                findings.append(Finding("ERROR", path, f"link target note not found: {link.group('note')}"))
            elif target not in blocks.get(block, []):
                findings.append(Finding("ERROR", path, f"link target block not found: {target.stem}#^{block.lower()}"))
            label = link.group("label")
            if label and label.upper() != block:
                findings.append(Finding("WARNING", path, f"link label '{label}' differs from {block}"))

        sol_name = SOL_NAME_RE.match(path.name)
        if sol_name:
            sol_id = sol_name.group(1).upper()
            metadata = parse_frontmatter(text)
            missing = sorted(REQUIRED_SOL_KEYS.difference(metadata))
            if missing:
                findings.append(Finding("ERROR", path, "missing SOL YAML keys: " + ", ".join(missing)))
            if metadata.get("solution_id", "").upper() != sol_id:
                findings.append(Finding("ERROR", path, f"solution_id must equal {sol_id}"))
            if sol_id not in [match.group(1).upper() for match in file_headings]:
                findings.append(Finding("ERROR", path, f"main heading for {sol_id} not found"))
            if path not in blocks.get(sol_id, []):
                findings.append(Finding("ERROR", path, f"block ^{sol_id.lower()} not found"))
            rq_match = re.search(r"RQ-\d{3}", metadata.get("related_rq", ""), re.IGNORECASE)
            if not rq_match:
                findings.append(Finding("ERROR", path, "related_rq does not contain an RQ-### ID"))
            else:
                rq_id = rq_match.group(0).upper()
                if rq_id not in headings:
                    findings.append(Finding("ERROR", path, f"related_rq target not found: {rq_id}"))
                rq_path = notes.get("research_questions")
                if rq_path and sol_id not in texts[rq_path]:
                    findings.append(Finding("WARNING", path, f"{rq_id} has no visible backlink text for {sol_id}"))

    if args.full:
        for identifier, paths in headings.items():
            if identifier not in blocks:
                findings.append(Finding("ERROR", paths[0], f"heading {identifier} has no matching block"))
        for identifier, paths in blocks.items():
            if identifier not in headings:
                findings.append(Finding("ERROR", paths[0], f"block ^{identifier.lower()} has no matching heading"))

    for finding in sorted(findings, key=lambda item: (item.level != "ERROR", str(item.path).lower(), item.message)):
        print(f"{finding.level}: {finding.path.relative_to(root)}: {finding.message}")

    errors = sum(item.level == "ERROR" for item in findings)
    warnings = sum(item.level == "WARNING" for item in findings)
    mode = "full" if args.full else "targeted"
    print(f"SUMMARY: mode={mode} files={len(targets)} errors={errors} warnings={warnings}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
