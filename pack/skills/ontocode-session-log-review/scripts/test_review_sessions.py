#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("review_sessions.py")


def write_session(path: Path, source, prompt: str, tools=(), aborts=0) -> None:
    rows = [
        {"type": "session_meta", "payload": {"originator": "ontocode-tui", "source": source}},
        {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        },
    ]
    rows.extend(
        {"type": "response_item", "payload": {"type": "function_call", "name": tool}}
        for tool in tools
    )
    rows.extend(
        {"type": "event_msg", "payload": {"type": "turn_aborted"}}
        for _ in range(aborts)
    )
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


class ReviewSessionsTest(unittest.TestCase):
    def test_roles_noise_workflows_and_text_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            day = root / "2026/08/17"
            day.mkdir(parents=True)
            write_session(
                day / "root.jsonl",
                "cli",
                "Continue until all tasks are done",
                tools=(
                    "mcp__ontoindex__gn_ensure_fresh",
                    "mcp__ontoindex__gn_ensure_fresh",
                    "mcp__ontoindex__gn_analyze_job",
                    "project_plan_validate",
                    "mcp__ontoindex__gn_verify_diff",
                ),
                aborts=1,
            )
            write_session(
                day / "delegated.jsonl",
                {"subagent": {"thread_spawn": {"parent_thread_id": "root"}}},
                "Execution-evidence correction only",
                tools=("list_agents", "wait_agent", "wait_agent", "close_agent"),
                aborts=2,
            )
            write_session(
                day / "noise.jsonl",
                "other",
                '<codex_internal_context source="goal">continue working toward the active thread goal',
                tools=("wait", "wait", "write_stdin"),
            )
            command = [
                "python3",
                str(SCRIPT),
                "--days",
                "1",
                "--end",
                "2026-08-17",
                "--sessions-dir",
                str(root),
            ]
            report = json.loads(subprocess.check_output(command + ["--json"], text=True))
            self.assertEqual(report["roles"], {"root": 1, "delegated": 1, "unknown": 1})
            self.assertEqual(report["substantive_user_parts"], 2)
            self.assertEqual(report["aborts_by_role"], {"root": 1, "delegated": 2, "unknown": 0})
            workflows = {row["name"]: row for row in report["workflows"]}
            self.assertEqual(workflows["plan-continuation"]["root_sessions"], 1)
            self.assertEqual(workflows["task-recovery"]["delegated_sessions"], 1)
            tools = {
                role: {row["name"]: row for row in rows}
                for role, rows in report["tools_by_role"].items()
            }
            self.assertEqual(
                tools["root"]["mcp__ontoindex__gn_ensure_fresh"],
                {"name": "mcp__ontoindex__gn_ensure_fresh", "calls": 2, "sessions": 1, "repeated_sessions": 1},
            )
            self.assertEqual(tools["delegated"]["wait_agent"]["repeated_sessions"], 1)
            clusters = {row["name"]: row["by_role"] for row in report["operation_clusters"]}
            self.assertEqual(
                clusters["ontoindex-freshness"]["root"],
                {"calls": 3, "sessions": 1, "repeated_sessions": 1},
            )
            self.assertEqual(
                clusters["agent-pool-supervision"]["delegated"],
                {"calls": 4, "sessions": 1, "repeated_sessions": 1},
            )
            self.assertEqual(
                clusters["background-job-wait"]["unknown"],
                {"calls": 3, "sessions": 1, "repeated_sessions": 1},
            )
            self.assertEqual(
                clusters["changed-scope-verification"]["root"],
                {"calls": 2, "sessions": 1, "repeated_sessions": 1},
            )
            text_output = subprocess.check_output(command, text=True)
            self.assertIn("workflows:", text_output)
            self.assertIn("top prompts:", text_output)
            self.assertIn("tools by role:", text_output)
            self.assertIn("operation clusters:", text_output)

    def test_delta_lifecycle_and_owner_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions/2026/08/17"
            sessions.mkdir(parents=True)
            write_session(sessions / "root.jsonl", "cli", "Continue until all tasks are done")
            skills = root / "skills/axel-plan-autopilot"
            skills.mkdir(parents=True)
            (skills / "SKILL.md").write_text("manager loop\ncontinue\n")
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"workflows": []}))
            lifecycle = root / "lifecycle.json"
            lifecycle.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "recommendations": [
                            {
                                "workflow": "plan-continuation",
                                "status": "IMPLEMENTED",
                                "owner_skill": "axel-plan-autopilot",
                                "evidence_terms": ["manager loop", "continue"],
                            }
                        ],
                    }
                )
            )
            output = root / "summary.json"
            command = [
                "python3", str(SCRIPT), "--days", "1", "--end", "2026-08-17",
                "--sessions-dir", str(root / "sessions"), "--baseline", str(baseline),
                "--lifecycle", str(lifecycle), "--skills-dir", str(root / "skills"),
                "--output", str(output), "--json",
            ]
            report = json.loads(subprocess.check_output(command, text=True))
            self.assertEqual(report["workflow_deltas"][0]["trend"], "NEW")
            self.assertEqual(report["workflow_deltas"][0]["recommendation_status"], "IMPLEMENTED")
            self.assertEqual(report["workflow_deltas"][0]["owner"]["status"], "MATCHED")
            saved = json.loads(output.read_text())
            self.assertNotIn("top_prompts", saved)
            self.assertEqual(saved["workflow_deltas"], report["workflow_deltas"])


if __name__ == "__main__":
    unittest.main()
