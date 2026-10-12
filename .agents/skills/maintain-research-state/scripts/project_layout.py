"""Shared project layout contract for blank and evidence-based initialization."""

from __future__ import annotations

import json
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"
CONFIG_PATH = ".agents/config/project-layout.json"
POLICY_PATH = ".agents/instructions/project-layout.md"
OUTPUT_ALIAS = re.compile(r"^(?:outputs?|out|results?)(?:[._-].*|\d+)?$", re.IGNORECASE)
ENVIRONMENT_DIRS = {".git", ".obsidian"}


def validate_folder(folder: Path, spec: dict) -> None:
    if folder.is_absolute() or folder.drive or ".." in folder.parts or not folder.parts:
        raise ValueError(f"folder must be a relative path within the project: {folder}")
    first = folder.parts[0].casefold()
    forbidden = {name.casefold() for name in spec["forbidden_roots"]}
    if first in forbidden or (first != "outputs" and OUTPUT_ALIAS.fullmatch(first)):
        raise ValueError(f"noncanonical project directory {folder}; use outputs/, sources/ or .work/")


def layout(root: Path, extra: list[Path]) -> tuple[dict, list[Path], dict[str, str]]:
    default = json.loads((ASSETS / "project-layout.json").read_text(encoding="utf-8-sig"))
    config = root / CONFIG_PATH
    spec = json.loads(config.read_text(encoding="utf-8-sig")) if config.is_file() else default
    if spec.get("schema_version") != 1 or spec.get("output_root") != "outputs":
        raise ValueError("project layout requires schema_version=1 and output_root=outputs")
    if not isinstance(spec.get("directories"), list) or not all(isinstance(p, str) for p in spec["directories"]):
        raise ValueError("project layout directories must be a list of relative paths")
    # A local preset may add categories, but cannot remove the namespace protection.
    spec["forbidden_roots"] = list(dict.fromkeys(default["forbidden_roots"] + spec.get("forbidden_roots", [])))
    folders = list(dict.fromkeys([Path(p) for p in default["directories"] + spec["directories"]] + extra))
    for folder in folders:
        validate_folder(folder, spec)
    existing_dirs = sorted(
        (entry for entry in root.iterdir() if entry.is_dir()), key=lambda entry: entry.name.casefold()
    ) if root.is_dir() else []
    registered = {folder.parts[0].casefold() for folder in folders} | ENVIRONMENT_DIRS
    for entry in existing_dirs:
        if (
            entry.name.casefold() in {p.casefold() for p in spec["forbidden_roots"]}
            or (entry.name.casefold() != "outputs" and OUTPUT_ALIAS.fullmatch(entry.name))
        ):
            raise ValueError(f"existing noncanonical directory requires migration first: {entry}")
        if entry.name.casefold() not in registered:
            if config.is_file():
                raise ValueError(f"register existing directory {entry.name} in {CONFIG_PATH} before initialization")
            # Keep lawful source directories in place and register them before any write.
            folder = Path(entry.name)
            validate_folder(folder, spec)
            folders.append(folder)
    if config.is_file():
        registered = {Path(folder).parts[0].casefold() for folder in spec["directories"]}
        if any(folder.parts[0].casefold() not in registered for folder in extra):
            raise ValueError(f"update {CONFIG_PATH} explicitly before adding a top-level category")
    else:
        spec["directories"] = [folder.as_posix() for folder in folders]
    documents = {
        CONFIG_PATH: json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
        POLICY_PATH: (ASSETS / "project-layout.template.md").read_text(encoding="utf-8-sig"),
        ".gitignore": (ASSETS / "gitignore.template").read_text(encoding="utf-8-sig"),
    }
    for name in list(documents):
        target = root / name
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f"layout control is not a regular file: {target}")
        if target.is_file():
            del documents[name]
    return spec, folders, documents


def findings(root: Path) -> list[str]:
    spec, folders, _ = layout(root, [])
    issues = [f"missing framework directory: {folder}" for folder in folders if not (root / folder).is_dir()]
    issues.extend(f"missing layout control: {name}" for name in (CONFIG_PATH, POLICY_PATH) if not (root / name).is_file())
    allowed = {folder.parts[0].casefold() for folder in folders} | ENVIRONMENT_DIRS
    issues.extend(
        f"unregistered top-level directory: {entry.name}"
        for entry in root.iterdir() if entry.is_dir() and entry.name.casefold() not in allowed
    )
    return issues


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Read-only validation of the project directory contract")
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    try:
        errors = findings(args.root.resolve())
        for message in errors:
            print(f"ERROR: {message}")
        print(f"LAYOUT: errors={len(errors)}")
        sys.exit(bool(errors))
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
