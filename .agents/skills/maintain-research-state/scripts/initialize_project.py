#!/usr/bin/env python3
"""Create blank research-state frames from the existing PPTX skill templates."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

from project_layout import CONFIG_PATH, POLICY_PATH, layout

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT.parent / "pptx-to-research-state" / "assets"
STATE_NAMES = ("CURRENT_STATE.md", "RESEARCH_QUESTIONS.md", "PROJECT_STORY.md")
OUTPUT_NAMES = (*STATE_NAMES, "AGENTS.md")
EXCLUDED_DIRS = {".agents", ".git", ".obsidian"}
ENTRY_RE = re.compile(
    r"^#{1,6}\s+(?:OBS|CON|HYP|RQ|SOL)-\d{3}\b|"
    r"^.*(?<![\w#])\^(?:obs|con|hyp|rq|sol)-\d{3}\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def occupied(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def agents_route_patch(root: Path) -> tuple[bytes, bytes] | None:
    """Preserve existing bytes; plan only a missing mandatory directory-policy entry."""
    path = root / "AGENTS.md"
    if not occupied(path):
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"AGENTS.md is not a regular file: {path}")
    original = path.read_bytes()
    text = re.sub(r"<!--.*?-->", "", original.decode("utf-8-sig"), flags=re.DOTALL)
    visible: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            if fence is None:
                fence = (marker.group(1)[0], len(marker.group(1)))
            elif marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1] and not marker.group(2).strip():
                fence = None
            continue
        if fence is None and not line.lstrip().startswith(">"):
            visible.append(line)
    for paragraph in re.split(r"\n\s*\n", "\n".join(visible)):
        if POLICY_PATH in paragraph and re.search(
            r"\b(?:read|follow|consult|must|required)\b|读取|遵循|必读|必须", paragraph, re.IGNORECASE
        ):
            return original, b""
    newline = "\r\n" if b"\r\n" in original else "\n"
    suffix = (
        ("" if original.endswith((b"\n\n", b"\r\n\r\n")) else newline if original.endswith(b"\n") else newline * 2)
        + "## Directory contract" + newline * 2
        + f"创建或移动文件前，必须读取 `{POLICY_PATH}` 并遵守目录合同；目录清单保存在 `{CONFIG_PATH}`。"
        + newline
    )
    return original, suffix.encode("utf-8")


def check_folders(root: Path, folders: list[Path]) -> None:
    if occupied(root) and not root.is_dir():
        raise ValueError(f"target is not a directory: {root}")
    for folder in folders:
        target = root / folder
        if not target.resolve().is_relative_to(root):
            raise ValueError(f"folder leaves project root: {folder}")
        for part in (target, *target.parents):
            if part == root:
                break
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError(f"folder crosses a directory link: {part}")
            if occupied(part) and not part.is_dir():
                raise ValueError(f"folder conflicts with an existing file: {part}")


def preflight(root: Path, folders: list[Path]) -> bool:
    """Refuse existing state; return whether an existing AGENTS must be preserved."""
    if occupied(root) and not root.is_dir():
        raise ValueError(f"target is not a directory: {root}")
    for name in STATE_NAMES:
        if occupied(root / name):
            raise ValueError(f"existing research state: {root / name}")
    agents = root / "AGENTS.md"
    if occupied(agents) and (agents.is_symlink() or not agents.is_file()):
        raise ValueError(f"AGENTS.md is not a regular file: {agents}")
    if root.exists():
        def scan_error(error: OSError) -> None:
            raise error

        for directory, subdirs, files in os.walk(root, followlinks=False, onerror=scan_error):
            subdirs[:] = [
                name for name in subdirs
                if name.casefold() not in EXCLUDED_DIRS
                and not (Path(directory) / name).is_symlink()
                and not (hasattr(Path(directory) / name, "is_junction") and (Path(directory) / name).is_junction())
            ]
            # Core filenames denote state even when a partial project left a directory.
            for name in files + subdirs:
                path = Path(directory) / name
                if name.casefold() in {item.casefold() for item in STATE_NAMES} or re.match(
                    r"^SOL-\d{3}(?:[_.-]|$)", name, re.IGNORECASE
                ):
                    raise ValueError(f"existing research state: {path}")
                if name.lower().endswith(".md") and name.casefold() != "agents.md":
                    if path.is_symlink():
                        raise ValueError(f"cannot check research state through a symbolic link: {path}")
                    if not path.is_file():
                        continue
                    if ENTRY_RE.search(path.read_text(encoding="utf-8-sig")):
                        raise ValueError(f"existing stable research entry: {path}")
    check_folders(root, folders)
    return agents.is_file()


def blank_note(template: str, date: str) -> str:
    """Keep template headings and document preamble; discard all example entries."""
    body = re.sub(r"\A---\n.*?\n---\n", "", template, count=1, flags=re.DOTALL)
    lines: list[str] = []
    in_preamble = True
    for line in body.splitlines():
        if line.startswith("## "):
            in_preamble = False
        if line.startswith("#"):
            if re.match(r"^#{1,6}\s+(?:OBS|CON|HYP|RQ|SOL)-\d{3}\b", line):
                continue
            if line.startswith("## Priority 1"):
                line = "## Priority 1"
            elif line.startswith("## Story 1"):
                line = "## 故事框架（待填写）"
            if "{{" in line:
                raise ValueError(f"unrecognized placeholder heading in template: {line}")
            lines.extend((line, ""))
        elif in_preamble and line.strip():
            lines.extend((line, ""))
    result = f"---\ndate: {date}\n---\n\n" + "\n".join(lines).rstrip() + "\n"
    first_section = result.index("\n## ")
    return (
        result[:first_section]
        + "\n<!-- 空白结构框架；正文待填写，尚未创建科研条目。 -->\n"
        + result[first_section:]
    )


def render_agents(template: str, root: Path, project_name: str, scope: str) -> str:
    text = template.replace("{{PROJECT_NAME}}", project_name).replace(
        "{{ONE_SENTENCE_PROJECT_SCOPE}}", scope or "研究范围待填写。"
    )
    routes = [
        "## Task routes", "",
        "只使用目标项目中实际存在的规则路径或当前可用技能。既有政策优先，不自动安装技能或复制依赖。", "",
    ]
    local = {
        name: f".agents/skills/{name}/SKILL.md"
        for name in (
            "maintain-research-state", "literature-source-gate",
            "academic-writing-editor", "pptx-to-research-state",
        )
        if (root / f".agents/skills/{name}/SKILL.md").is_file()
    }
    if "maintain-research-state" in local:
        routes.append(
            f"- 空白初始化与结构维护：读取 `{local['maintain-research-state']}` 的对应分支；"
            "已有科研状态时不执行空白初始化，未经明确要求不补齐或重建。"
        )
    else:
        routes.append(
            "- 空白初始化：仅在明确要求建立新项目框架且没有既有科研状态时执行；"
            "保留已有 AGENTS.md 规则，只补齐缺失的目录合同入口。结构维护使用下方精简结构合同，手动核对受影响条目，"
            "合并修改后检查一次，不默认全库审计。"
        )
    if "literature-source-gate" in local:
        routes.append(
            f"- 外部文献：先读取 `{local['literature-source-gate']}`，执行其来源和引用政策。"
            "强制政策缺失时暂停依赖它的部分，不自行放宽门槛。"
        )
    else:
        routes.append(
            "- 外部文献：核验身份、原文支持和来源状态，区分直接/间接/推测；"
            "不拼接不同体系为已证明机制，不补造来源或指标。后续建立的项目来源政策优先。"
        )
    editor = local.get("academic-writing-editor")
    routes.append(
        f"- 学术正文：先读取 `{editor}`，事实与结构完成后再编辑。" if editor else
        "- 学术正文：可用时使用 academic-writing-editor，事实与结构完成后再编辑；"
        "一般正文缺少该技能时使用下方写作底线，SOL 最终编辑仍须该技能，缺少时停止最终 SOL 生成。"
    )
    if "pptx-to-research-state" in local:
        routes.append(
            f"- 从 PPTX 导入科研状态：读取 `{local['pptx-to-research-state']}` 的对应分支；"
            "已有项目增量更新，不重新初始化。"
        )
    else:
        routes.append(
            "- 从 PPTX 导入科研状态：当前可用时使用 pptx-to-research-state 对应分支；"
            "否则另行选择具备结构提取与视觉核对能力的工具，不能以空白框架替代证据导入。"
        )
    routes.append(
        "- 文件制作：用户选择和现有专用管线优先，否则使用当前可用文档工具；同一任务选择一个实现入口。"
    )
    text, count = re.subn(
        r"^## Task routes\n.*?(?=^## )", "\n".join(routes) + "\n\n", text,
        count=1, flags=re.MULTILINE | re.DOTALL,
    )
    if count != 1:
        raise ValueError("AGENTS template is missing the Task routes section")
    story_rule = (
        "详细职责遵循项目故事政策及当前 pptx-to-research-state 的故事工作流与模板；"
        "生成本文件时解析其实际可用路径。"
    )
    if story_rule not in text:
        raise ValueError("AGENTS template story routing has changed; review the renderer")
    story_paths = [
        path for path in (
            ".agents/instructions/story-policy.md",
            ".agents/skills/pptx-to-research-state/references/story-workflow.md",
        ) if (root / path).is_file()
    ]
    story_route = (
        "详细职责遵循 " + " 和 ".join(f"`{path}`" for path in story_paths) + "。"
        if story_paths else "各节按下方职责和证据边界填写。"
    )
    text = text.replace(story_rule, story_route)
    return text


def render(root: Path, date: str, name: str, scope: str, preserve_agents: bool) -> dict[str, str]:
    outputs = {}
    for filename in OUTPUT_NAMES:
        if filename == "AGENTS.md" and preserve_agents:
            continue
        source = TEMPLATE_ROOT / filename.replace(".md", ".template.md")
        template = source.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        outputs[filename] = (
            render_agents(template, root, name, scope)
            if filename == "AGENTS.md" else blank_note(template, date)
        )
        if re.search(r"\{\{[^\n]*?\}\}", outputs[filename]):
            raise ValueError(f"unresolved template variable: {filename}")
    return outputs


def create(
    root: Path, outputs: dict[str, str], folders: list[Path],
    agents_patch: tuple[bytes, bytes] | None = None,
) -> tuple[list[Path], list[Path]]:
    files_created: list[Path] = []
    dirs_created: list[Path] = []
    agents_append_started = False

    def check_agents() -> None:
        if agents_patch is not None:
            path = root / "AGENTS.md"
            if path.is_symlink() or not path.is_file() or path.read_bytes() != agents_patch[0]:
                raise ValueError("AGENTS.md changed during preflight; re-read target instructions")

    def mkdir(path: Path) -> None:
        if path.is_dir():
            return
        mkdir(path.parent)
        path.mkdir()
        dirs_created.append(path)

    try:
        check_agents()
        mkdir(root)
        for name, text in outputs.items():
            path = root / name
            mkdir(path.parent)
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                files_created.append(path)
                handle.write(text)
        for folder in folders:
            mkdir(root / folder)
        if agents_patch is not None:
            check_agents()
            original, suffix = agents_patch
            if suffix:
                with (root / "AGENTS.md").open("r+b") as handle:
                    if handle.read() != original:
                        raise ValueError("AGENTS.md changed during preflight; re-read target instructions")
                    agents_append_started = True
                    handle.write(suffix)
    except Exception:
        if agents_append_started and agents_patch is not None:
            original, suffix = agents_patch
            path = root / "AGENTS.md"
            current = path.read_bytes()
            if len(current) >= len(original) and (original + suffix).startswith(current):
                with path.open("r+b") as handle:
                    handle.truncate(len(original))
        # Roll back only paths exclusively created by this invocation.
        for path in reversed(files_created):
            path.unlink()
        for path in reversed(dirs_created):
            try:
                path.rmdir()
            except OSError:
                pass  # Preserve any concurrent content.
        raise
    return files_created, dirs_created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Target project directory")
    parser.add_argument("--date", required=True, help="Current date in the user's timezone, YYYY-MM-DD")
    parser.add_argument("--project-name", help="Default: target directory name")
    parser.add_argument("--scope", default="", help="User-supplied one-sentence scope; otherwise left unfilled")
    parser.add_argument("--folder", action="append", default=[], type=Path, help="Optional relative folder, repeatable")
    parser.add_argument("--check", action="store_true", help="Read-only preflight and output preview")
    parser.add_argument("--layout-only", action="store_true", help="Create only missing layout controls and directories; preserve all research files")
    args = parser.parse_args()
    try:
        if dt.date.fromisoformat(args.date).isoformat() != args.date:
            raise ValueError("date must use YYYY-MM-DD")
        if args.root.is_symlink():
            raise ValueError("target root must not be a symbolic link")
        root = args.root.resolve()
        name = args.project_name or root.name
        if any(character in name + args.scope for character in "\r\n"):
            raise ValueError("project name and scope must each be a single line")
        for folder in args.folder:
            if folder.is_absolute() or folder.drive or ".." in folder.parts:
                raise ValueError(f"folder must be a relative path within the project: {folder}")
            if any(part.casefold() in {name.casefold() for name in OUTPUT_NAMES} for part in folder.parts):
                raise ValueError(f"folder conflicts with an output filename: {folder}")
        _, folders, controls = layout(root, args.folder)
        if args.layout_only:
            check_folders(root, folders)
            preserve_agents = (root / "AGENTS.md").is_file()
            outputs = controls
        else:
            preserve_agents = preflight(root, folders)
            outputs = render(root, args.date, name, args.scope, preserve_agents)
            outputs.update(controls)
        agents_patch = agents_route_patch(root)
        if args.check:
            print(f"READY: {root}")
            for filename in outputs:
                print(f"WOULD CREATE: {filename}")
            for folder in folders:
                print(f"FOLDER: {folder}")
            if agents_patch is not None and agents_patch[1]:
                print("WOULD APPEND: AGENTS.md directory-contract entry")
        else:
            # Repeat immediately before mutation, protecting against state added during rendering.
            if not args.layout_only and preflight(root, folders) != preserve_agents:
                raise ValueError("AGENTS.md changed during preflight; re-read target instructions")
            if args.layout_only:
                check_folders(root, folders)
            _, latest_folders, latest_controls = layout(root, args.folder)
            if latest_folders != folders or latest_controls != controls:
                raise ValueError("project layout changed during preflight; re-check before creating files")
            files, directories = create(root, outputs, folders, agents_patch)
            for path in files:
                print(f"CREATED: {path}")
            for path in directories:
                print(f"CREATED DIRECTORY: {path}")
            if agents_patch is not None and agents_patch[1]:
                print(f"APPENDED DIRECTORY-CONTRACT ENTRY: {root / 'AGENTS.md'}")
        if preserve_agents:
            print(f"PRESERVED EXISTING RULES: {root / 'AGENTS.md'}")
        print(f"DIRECTORY POLICY: {root / POLICY_PATH}")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
