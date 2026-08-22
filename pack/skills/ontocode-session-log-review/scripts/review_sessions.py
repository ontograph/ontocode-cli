#!/usr/bin/env python3
"""Summarize bounded Ontocode rollout logs without failing on malformed lines."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


NOISE_PREFIXES = (
    "# AGENTS.md instructions",
    "v1\n\n## User Profile",
    "Authoritative manager-loop dispatch packet",
    "<environment_context>",
    "<internal_goal_context>",
    "<codex_internal_context",
    "<subagent_notification>",
    "<turn_aborted>",
)
CONTROL_TEXT = {"hi", "v1", "ignore", "reply exactly ok", "ok"}
WORKFLOW_PATTERNS = {
    "plan-continuation": (
        r"\bcontinue\b",
        r"\bwhat is left\b",
        r"\bopen tasks?\b",
        r"\bproceed .*tasks?\b",
        r"\bcoder-manager\b",
    ),
    "task-recovery": (
        r"\bunblock\b",
        r"\bresume .*lease\b",
        r"\bprevious result was rejected\b",
        r"\bexecution-evidence correction\b",
    ),
    "session-log-review": (
        r"\bsession logs?\b",
        r"\bsession review\b",
        r"\boffline diagn",
    ),
    "disk-build-recovery": (r"\bcheck space\b", r"\bdisk space\b"),
    "qt-native-grid-evidence": (r"\bnative.grid\b", r"\brun-qt\b", r"\bxdotool\b"),
    "worktree-task-packet": (r"\bworktree\b", r"\btask packet\b", r"\bwrite set\b"),
}
OPERATION_CLUSTERS = {
    "ontoindex-freshness": {"mcp__ontoindex__gn_ensure_fresh", "mcp__ontoindex__gn_analyze_job"},
    "agent-pool-supervision": {"list_agents", "wait_agent", "close_agent", "send_message"},
    "background-job-wait": {"wait", "write_stdin"},
    "changed-scope-verification": {"project_plan_validate", "mcp__ontoindex__gn_verify_diff"},
}
ROLES = ("root", "delegated", "unknown")
LIFECYCLE_STATUSES = {"NEW", "SELECTED", "IMPLEMENTED", "REJECTED", "SUPERSEDED"}
DEFAULT_LIFECYCLE = Path(__file__).parent.parent / "references/recommendation-lifecycle.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    parser.add_argument("--sessions-dir", type=Path, default=Path.home() / ".ontocode/sessions")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--lifecycle", type=Path, default=DEFAULT_LIFECYCLE)
    parser.add_argument("--skills-dir", type=Path, action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def iter_files(root: Path, start: date, end: date):
    for offset in range((end - start).days + 1):
        day = start + timedelta(days=offset)
        yield from sorted((root / day.strftime("%Y/%m/%d")).glob("*.jsonl"))


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def session_role(payload: dict) -> str:
    source = payload.get("source")
    if source == "cli":
        return "root"
    if isinstance(source, dict) and isinstance(source.get("subagent"), dict):
        return "delegated"
    return "unknown"


def matching_workflows(prompts: set[str]) -> set[str]:
    matches = set()
    for workflow, patterns in WORKFLOW_PATTERNS.items():
        if any(re.search(pattern, prompt) for prompt in prompts for pattern in patterns):
            matches.add(workflow)
    return matches


def load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"invalid {label}: {path}: {error}") from error
    if not isinstance(value, dict):
        raise SystemExit(f"invalid {label}: {path}: expected JSON object")
    return value


def workflow_map(report: dict) -> dict[str, dict]:
    return {
        row["name"]: row
        for row in report.get("workflows", [])
        if isinstance(row, dict) and isinstance(row.get("name"), str)
    }


def lifecycle_entries(path: Path) -> dict[str, dict]:
    data = load_json(path, "recommendation lifecycle")
    if data.get("version") != 1 or not isinstance(data.get("recommendations"), list):
        raise SystemExit(f"invalid recommendation lifecycle: {path}: expected version 1 recommendations")
    entries = {}
    for row in data["recommendations"]:
        if not isinstance(row, dict) or not isinstance(row.get("workflow"), str):
            raise SystemExit(f"invalid recommendation lifecycle: {path}: invalid recommendation")
        status = row.get("status")
        if status not in LIFECYCLE_STATUSES:
            raise SystemExit(f"invalid recommendation lifecycle: {path}: invalid status {status!r}")
        entries[row["workflow"]] = row
    return entries


def verify_owner(row: dict, skill_dirs: list[Path]) -> dict:
    owner = row.get("owner_skill")
    if not owner:
        return {"status": "NO_OWNER"}
    skill_file = next((root / owner / "SKILL.md" for root in skill_dirs if (root / owner / "SKILL.md").is_file()), None)
    if skill_file is None:
        return {"status": "MISSING_SKILL", "skill": owner}
    content = skill_file.read_text(errors="replace").lower()
    terms = [str(term).lower() for term in row.get("evidence_terms", [])]
    missing = [term for term in terms if term not in content]
    return {
        "status": "CONTENT_MISMATCH" if missing else "MATCHED",
        "skill": owner,
        "skill_file": str(skill_file),
        "missing_terms": missing,
    }


def build_deltas(current: dict, baseline: dict, lifecycle: dict[str, dict], skill_dirs: list[Path]) -> list[dict]:
    current_rows = workflow_map(current)
    baseline_rows = workflow_map(baseline)
    names = set(current_rows) | set(baseline_rows) | set(lifecycle)
    deltas = []
    for name in names:
        current_row = current_rows.get(name, {})
        baseline_row = baseline_rows.get(name, {})
        current_total = sum(current_row.get(field, 0) for field in ("root_sessions", "delegated_sessions", "unknown_sessions"))
        baseline_total = sum(baseline_row.get(field, 0) for field in ("root_sessions", "delegated_sessions", "unknown_sessions"))
        if baseline_total == 0 and current_total > 0:
            trend = "NEW"
        elif current_total > baseline_total:
            trend = "INCREASING"
        elif current_total < baseline_total:
            trend = "DECREASING"
        else:
            trend = "UNCHANGED"
        lifecycle_row = lifecycle.get(name, {})
        deltas.append(
            {
                "name": name,
                "trend": trend,
                "current_sessions": current_total,
                "baseline_sessions": baseline_total,
                "delta_sessions": current_total - baseline_total,
                "recommendation_status": lifecycle_row.get("status", "NEW"),
                "owner": verify_owner(lifecycle_row, skill_dirs),
            }
        )
    return sorted(deltas, key=lambda row: (-row["current_sessions"], row["name"]))


def sanitized_snapshot(report: dict) -> dict:
    return {key: value for key, value in report.items() if key != "top_prompts"}


def metric_rows(calls: Counter[str], sessions: Counter[str], repeated: Counter[str]) -> list[dict]:
    return [
        {
            "name": name,
            "calls": calls[name],
            "sessions": sessions[name],
            "repeated_sessions": repeated[name],
        }
        for name in sorted(calls, key=lambda item: (-calls[item], -sessions[item], item))[:20]
    ]


def main() -> int:
    args = parse_args()
    if args.days < 1:
        raise SystemExit("--days must be positive")
    start = args.end - timedelta(days=args.days - 1)
    files = list(iter_files(args.sessions_dir, start, args.end))
    prompts: Counter[str] = Counter()
    tool_calls: Counter[str] = Counter()
    tool_sessions: Counter[str] = Counter()
    origins: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    aborts_by_role: Counter[str] = Counter()
    tool_calls_by_role = {role: Counter() for role in ROLES}
    tool_sessions_by_role = {role: Counter() for role in ROLES}
    repeated_tool_sessions_by_role = {role: Counter() for role in ROLES}
    cluster_calls_by_role = {role: Counter() for role in ROLES}
    cluster_sessions_by_role = {role: Counter() for role in ROLES}
    repeated_cluster_sessions_by_role = {role: Counter() for role in ROLES}
    workflow_root: Counter[str] = Counter()
    workflow_delegated: Counter[str] = Counter()
    workflow_unknown: Counter[str] = Counter()
    malformed = user_records = substantive = aborts = total_bytes = 0
    files_grew = bytes_growth = 0

    for path in files:
        initial_size = path.stat().st_size
        total_bytes += initial_size
        origin = "unknown"
        role = "unknown"
        session_prompts: set[str] = set()
        session_tools: Counter[str] = Counter()
        session_aborts = 0
        for raw in path.open(encoding="utf-8", errors="replace"):
            try:
                item = json.loads(raw)
            except json.JSONDecodeError:
                malformed += 1
                continue
            payload = item.get("payload", {})
            if item.get("type") == "session_meta":
                origin = payload.get("originator") or "unknown"
                role = session_role(payload)
            elif item.get("type") == "event_msg" and payload.get("type") == "turn_aborted":
                session_aborts += 1
            elif item.get("type") == "response_item" and payload.get("type") == "function_call":
                name = payload.get("name") or "unknown"
                session_tools[name] += 1
            elif (
                item.get("type") == "response_item"
                and payload.get("type") == "message"
                and payload.get("role") == "user"
            ):
                user_records += 1
                for part in payload.get("content", []):
                    text = part.get("text", "") if isinstance(part, dict) else ""
                    folded = normalize(text)
                    if not text or text.startswith(NOISE_PREFIXES) or folded in CONTROL_TEXT:
                        continue
                    substantive += 1
                    shortened = folded[:160]
                    prompts[shortened] += 1
                    session_prompts.add(shortened)
        origins[origin] += 1
        roles[role] += 1
        aborts += session_aborts
        aborts_by_role[role] += session_aborts
        tool_calls.update(session_tools)
        tool_sessions.update(session_tools.keys())
        tool_calls_by_role[role].update(session_tools)
        tool_sessions_by_role[role].update(session_tools.keys())
        repeated_tool_sessions_by_role[role].update(
            name for name, count in session_tools.items() if count > 1
        )
        for cluster, names in OPERATION_CLUSTERS.items():
            calls = sum(session_tools[name] for name in names)
            if calls:
                cluster_calls_by_role[role][cluster] += calls
                cluster_sessions_by_role[role][cluster] += 1
                repeated_cluster_sessions_by_role[role][cluster] += calls > 1
        role_counter = {
            "root": workflow_root,
            "delegated": workflow_delegated,
            "unknown": workflow_unknown,
        }[role]
        role_counter.update(matching_workflows(session_prompts))
        final_size = path.stat().st_size
        if final_size > initial_size:
            files_grew += 1
            bytes_growth += final_size - initial_size

    workflows = []
    for name in sorted(
        WORKFLOW_PATTERNS,
        key=lambda item: (-workflow_root[item], -workflow_delegated[item], item),
    ):
        total = workflow_root[name] + workflow_delegated[name] + workflow_unknown[name]
        if total:
            workflows.append(
                {
                    "name": name,
                    "root_sessions": workflow_root[name],
                    "delegated_sessions": workflow_delegated[name],
                    "unknown_sessions": workflow_unknown[name],
                }
            )

    report = {
        "window": {"start": start.isoformat(), "end": args.end.isoformat(), "days": args.days},
        "files": len(files),
        "bytes": total_bytes,
        "origins": dict(origins.most_common()),
        "roles": dict(roles.most_common()),
        "live_growth": {"files": files_grew, "bytes": bytes_growth},
        "malformed_lines": malformed,
        "user_records": user_records,
        "substantive_user_parts": substantive,
        "turn_aborted": aborts,
        "aborts_by_role": {role: aborts_by_role[role] for role in ROLES},
        "workflows": workflows,
        "top_prompts": prompts.most_common(20),
        "top_tools_by_sessions": tool_sessions.most_common(20),
        "top_tools": tool_calls.most_common(20),
        "tools_by_role": {
            role: metric_rows(
                tool_calls_by_role[role],
                tool_sessions_by_role[role],
                repeated_tool_sessions_by_role[role],
            )
            for role in ROLES
        },
        "operation_clusters": [
            {
                "name": cluster,
                "tools": sorted(names),
                "by_role": {
                    role: {
                        "calls": cluster_calls_by_role[role][cluster],
                        "sessions": cluster_sessions_by_role[role][cluster],
                        "repeated_sessions": repeated_cluster_sessions_by_role[role][cluster],
                    }
                    for role in ROLES
                },
            }
            for cluster, names in OPERATION_CLUSTERS.items()
        ],
    }
    skill_dirs = args.skills_dir or [Path.home() / ".ontocode/skills", Path.home() / ".agents/skills"]
    lifecycle = lifecycle_entries(args.lifecycle)
    report["recommendation_lifecycle"] = [
        {
            "workflow": name,
            "status": row["status"],
            "owner": verify_owner(row, skill_dirs),
        }
        for name, row in sorted(lifecycle.items())
    ]
    if args.baseline:
        report["delta_from"] = str(args.baseline)
        report["workflow_deltas"] = build_deltas(report, load_json(args.baseline, "baseline"), lifecycle, skill_dirs)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(sanitized_snapshot(report), indent=2) + "\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"window: {start}..{args.end} ({args.days} days)")
        print(f"files: {len(files)}  bytes: {total_bytes}  malformed_lines: {malformed}")
        print(f"origins: {dict(origins.most_common())}")
        print(f"roles: {dict(roles.most_common())}  live_growth: files={files_grew} bytes={bytes_growth}")
        print(
            f"user_records: {user_records}  substantive_parts: {substantive}  "
            f"turn_aborted: {aborts}  aborts_by_role: {report['aborts_by_role']}"
        )
        print("workflows:")
        for workflow in workflows:
            print(
                f"  {workflow['root_sessions']:4d} root  "
                f"{workflow['delegated_sessions']:4d} delegated  "
                f"{workflow['unknown_sessions']:4d} unknown  {workflow['name']}"
            )
        if args.baseline:
            print("workflow deltas:")
            for row in report["workflow_deltas"]:
                print(
                    f"  {row['delta_sessions']:+4d}  {row['trend']:<10}  "
                    f"{row['recommendation_status']:<11}  {row['name']}"
                )
        print("top prompts:")
        for prompt, count in prompts.most_common(20):
            print(f"  {count:4d}  {prompt}")
        print("tools by role:")
        for role, rows in report["tools_by_role"].items():
            for row in rows:
                print(
                    f"  {role:<9} {row['calls']:4d} calls  {row['sessions']:4d} sessions  "
                    f"{row['repeated_sessions']:4d} repeated  {row['name']}"
                )
        print("operation clusters:")
        for cluster in report["operation_clusters"]:
            for role, counts in cluster["by_role"].items():
                print(
                    f"  {role:<9} {counts['calls']:4d} calls  {counts['sessions']:4d} sessions  "
                    f"{counts['repeated_sessions']:4d} repeated  {cluster['name']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
