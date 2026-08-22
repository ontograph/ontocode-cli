#!/usr/bin/env python3
"""Watch one process and emit state changes instead of unchanged polls."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--status", type=Path)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=3600.0)
    parser.add_argument("--stall", type=float, default=900.0)
    parser.add_argument("--tail-lines", type=int, default=20)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def snapshot(path: Path | None):
    if path is None or not path.exists():
        return None
    stat = path.stat()
    return (stat.st_size, stat.st_mtime_ns)


def tail(path: Path, lines: int) -> list[str]:
    if not path.exists() or lines <= 0:
        return []
    block_size = 8192
    with path.open("rb") as stream:
        stream.seek(0, os.SEEK_END)
        position = stream.tell()
        chunks: list[bytes] = []
        line_count = 0
        while position > 0 and line_count <= lines:
            size = min(block_size, position)
            position -= size
            stream.seek(position)
            chunk = stream.read(size)
            chunks.append(chunk)
            line_count += chunk.count(b"\n")
    return b"".join(reversed(chunks)).decode("utf-8", errors="replace").splitlines()[-lines:]


def emit(value: dict, quiet: bool = False) -> None:
    if not quiet:
        print(json.dumps(value), flush=True)


def main() -> int:
    args = parse_args()
    if args.interval <= 0 or args.timeout <= 0 or args.stall <= 0:
        raise SystemExit("interval, timeout, and stall must be positive")
    started = last_change = time.monotonic()
    previous = (snapshot(args.log), snapshot(args.status), alive(args.pid))
    changes = 0

    if previous[0] is None and not previous[2]:
        classification = "MISSING"
    else:
        classification = "COMPLETED"
        while True:
            elapsed = time.monotonic() - started
            current = (snapshot(args.log), snapshot(args.status), alive(args.pid))
            if current != previous:
                changes += 1
                last_change = time.monotonic()
                emit({"event": "change", "elapsed_seconds": round(elapsed, 1),
                      "log": current[0], "status": current[1], "alive": current[2]}, args.quiet)
                previous = current
            if not current[2]:
                break
            if elapsed >= args.timeout:
                classification = "TIMED_OUT"
                break
            if time.monotonic() - last_change >= args.stall:
                classification = "STALLED"
                break
            time.sleep(args.interval)

    status_text = None
    if args.status and args.status.exists():
        status_text = args.status.read_text(encoding="utf-8", errors="replace").strip()[-1000:]
    if classification == "COMPLETED" and status_text and re_failure(status_text):
        classification = "FAILED"
    summary = {
        "event": "summary",
        "classification": classification,
        "pid": args.pid,
        "elapsed_seconds": round(time.monotonic() - started, 1),
        "changes": changes,
        "log": str(args.log),
        "log_bytes": args.log.stat().st_size if args.log.exists() else None,
        "status": str(args.status) if args.status else None,
        "status_text": status_text,
        "tail": tail(args.log, args.tail_lines),
    }
    print(json.dumps(summary), flush=True)
    return 0 if classification == "COMPLETED" else 1


def re_failure(text: str) -> bool:
    folded = text.lower()
    return bool(re.search(r"(?:exit|exit_code)\s*=\s*[1-9]\d*", folded)) or any(
        marker in folded for marker in ("failed", "result=fail")
    )


if __name__ == "__main__":
    raise SystemExit(main())
