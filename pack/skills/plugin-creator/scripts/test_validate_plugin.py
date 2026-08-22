#!/usr/bin/env python3
"""Boundary tests for plugin manifest validation."""

import json
import tempfile
import unittest
from pathlib import Path

from validate_plugin import validate_plugin


def write_plugin(root: Path, default_prompt: str) -> None:
    manifest_dir = root / ".codex-plugin"
    manifest_dir.mkdir()
    manifest = {
        "name": "prompt-boundary",
        "version": "1.0.0",
        "description": "Prompt boundary fixture",
        "interface": {
            "displayName": "Prompt Boundary",
            "shortDescription": "Prompt boundary fixture",
            "longDescription": "Prompt boundary fixture",
            "developerName": "Ontocode",
            "category": "Productivity",
            "capabilities": [],
            "defaultPrompt": default_prompt,
        },
        "author": {"name": "Ontocode"},
    }
    (manifest_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")


class DefaultPromptLengthTests(unittest.TestCase):
    def test_normalized_128_character_prompt_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_plugin(root, f"{'a' * 63}   {'b' * 64}")

            self.assertEqual(validate_plugin(root), [])

    def test_normalized_129_character_prompt_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_plugin(root, "a" * 129)

            self.assertEqual(
                validate_plugin(root),
                [
                    "plugin.json field `interface.defaultPrompt` must be at most "
                    "128 characters"
                ],
            )


if __name__ == "__main__":
    unittest.main()
