"""Behavioral regressions for directory registration and existing instruction updates."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import initialize_project as initializer
import project_layout


class InitializationCompatibility(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="research-init-regression-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"

    def run_initializer(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(SCRIPTS / "initialize_project.py"),
             "--root", str(self.root), "--date", "2026-10-12", *args],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def put(self, name: str, content: bytes) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def snapshot(self) -> dict[str, bytes]:
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_existing_source_directories_are_registered_without_moving_data(self) -> None:
        raw = self.put("data/raw/acquisition.bin", b"unchanged raw source")
        note = self.put("lab-notes/session.md", b"ordinary note; no stable research IDs")
        (self.root / ".git").mkdir()
        before = self.snapshot()
        self.run_initializer("--check")
        self.assertEqual(before, self.snapshot())
        self.run_initializer()
        self.assertEqual(raw.read_bytes(), before["data/raw/acquisition.bin"])
        self.assertEqual(note.read_bytes(), before["lab-notes/session.md"])
        config = json.loads((self.root / project_layout.CONFIG_PATH).read_text(encoding="utf-8"))
        self.assertIn("data", config["directories"])
        self.assertIn("lab-notes", config["directories"])
        self.assertNotIn(".git", config["directories"])
        self.assertEqual(project_layout.findings(self.root), [])

    def test_unregistered_directory_with_existing_config_stops_before_any_write(self) -> None:
        source = project_layout.ASSETS / "project-layout.json"
        self.put(project_layout.CONFIG_PATH, source.read_bytes())
        self.put("data/raw.bin", b"keep data")
        self.put("AGENTS.md", b"# Existing rules\n")
        before = self.snapshot()
        result = self.run_initializer(expected=2)
        self.assertIn("register existing directory data", result.stderr)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / "CURRENT_STATE.md").exists())

    def test_existing_agents_gets_only_missing_route_and_is_idempotent(self) -> None:
        original = b"\xef\xbb\xbf# Existing rules\r\n\r\nKeep every original byte.\r\n"
        agents = self.put("AGENTS.md", original)
        preview = self.run_initializer("--check")
        self.assertIn("WOULD APPEND", preview.stdout)
        self.assertEqual(agents.read_bytes(), original)
        self.run_initializer()
        updated = agents.read_bytes()
        self.assertTrue(updated.startswith(original))
        self.assertIn(project_layout.POLICY_PATH.encode(), updated[len(original):])
        self.assertNotIn(b"\n", updated[len(original):].replace(b"\r\n", b""))
        before = self.snapshot()
        self.run_initializer("--layout-only")
        self.assertEqual(before, self.snapshot())
        self.assertEqual(project_layout.findings(self.root), [])

    def test_existing_live_route_is_preserved_byte_for_byte(self) -> None:
        original = ("# Existing rules\n\nBefore creating files, read `"
                    + project_layout.POLICY_PATH + "`.\n").encode()
        agents = self.put("AGENTS.md", original)
        preview = self.run_initializer("--check")
        self.assertNotIn("WOULD APPEND", preview.stdout)
        self.run_initializer()
        self.assertEqual(agents.read_bytes(), original)

    def test_example_and_comment_paths_do_not_suppress_required_entry(self) -> None:
        original = (
            "# Existing rules\n\n<!-- Must read `" + project_layout.POLICY_PATH + "` -->\n"
            "\n````markdown\n```\nMust read `" + project_layout.POLICY_PATH + "`\n````\n"
            "\n> Must read `" + project_layout.POLICY_PATH + "`\n"
        ).encode()
        agents = self.put("AGENTS.md", original)
        self.run_initializer()
        self.assertTrue(agents.read_bytes().startswith(original))
        self.assertIn(project_layout.POLICY_PATH.encode(), agents.read_bytes()[len(original):])

    def test_layout_only_adds_route_without_changing_research_files(self) -> None:
        agents = self.put("AGENTS.md", b"# Existing rules\n")
        state = self.put("CURRENT_STATE.md", b"# Recorded state\n\n### OBS-007\n\nOriginal result. ^obs-007\n")
        original = state.read_bytes()
        self.run_initializer("--layout-only")
        self.assertEqual(state.read_bytes(), original)
        self.assertIn(project_layout.POLICY_PATH.encode(), agents.read_bytes())
        self.assertFalse((self.root / "RESEARCH_QUESTIONS.md").exists())

    def test_legacy_output_aliases_still_stop_before_any_write(self) -> None:
        for alias in ("output", "outputs2", "out", "results", "tmp", "staging"):
            with self.subTest(alias=alias):
                directory = self.root / alias
                directory.mkdir(parents=True)
                before = self.snapshot()
                self.run_initializer(expected=2)
                self.assertEqual(before, self.snapshot())
                self.assertEqual(list(self.root.iterdir()), [directory])
                directory.rmdir()

    def test_existing_research_state_still_blocks_blank_initialization(self) -> None:
        agents = self.put("AGENTS.md", b"# Existing rules\n")
        self.put("CURRENT_STATE.md", b"")
        before = self.snapshot()
        self.run_initializer(expected=2)
        self.assertEqual(before, self.snapshot())
        self.assertNotIn(project_layout.POLICY_PATH.encode(), agents.read_bytes())

    def test_concurrent_agents_edit_rolls_back_only_new_files(self) -> None:
        agents = self.put("AGENTS.md", b"# Existing rules\n")
        planned = initializer.agents_route_patch(self.root)
        newer = agents.read_bytes() + b"New human instruction.\n"
        real_mkdir = Path.mkdir

        def edit_after_creation(path: Path, *args, **kwargs):
            result = real_mkdir(path, *args, **kwargs)
            if path == self.root / "later":
                agents.write_bytes(newer)
            return result

        with patch.object(Path, "mkdir", edit_after_creation):
            with self.assertRaisesRegex(ValueError, "AGENTS.md changed"):
                initializer.create(self.root, {"CURRENT_STATE.md": "new"}, [Path("later")], planned)
        self.assertEqual(agents.read_bytes(), newer)
        self.assertFalse((self.root / "CURRENT_STATE.md").exists())
        self.assertFalse((self.root / "later").exists())

    def test_partial_append_error_restores_original_and_rolls_back_new_files(self) -> None:
        agents = self.put("AGENTS.md", b"# Existing rules\n")
        original = agents.read_bytes()
        planned = initializer.agents_route_patch(self.root)
        real_open = Path.open
        injected = False

        class PartialWrite:
            def __init__(self, handle):
                self.handle = handle
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.handle.close()
            def read(self):
                return self.handle.read()
            def write(self, data):
                self.handle.write(data[:len(data) // 2])
                self.handle.flush()
                raise OSError("injected append failure")

        def open_with_failure(path: Path, mode="r", *args, **kwargs):
            nonlocal injected
            handle = real_open(path, mode, *args, **kwargs)
            if path == agents and mode == "r+b" and not injected:
                injected = True
                return PartialWrite(handle)
            return handle

        with patch.object(Path, "open", open_with_failure):
            with self.assertRaisesRegex(OSError, "injected append failure"):
                initializer.create(self.root, {"CURRENT_STATE.md": "new"}, [], planned)
        self.assertEqual(agents.read_bytes(), original)
        self.assertFalse((self.root / "CURRENT_STATE.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
