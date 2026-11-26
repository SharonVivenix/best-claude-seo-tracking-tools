#!/usr/bin/env python3
"""
Send tracked prompts to Claude with the web search tool on and log what comes back.

    export ANTHROPIC_API_KEY=...
    python tracker/track.py tracker/prompts.example.json            # append to runs.jsonl
    python tracker/track.py tracker/prompts.example.json --dry-run  # parse examples/sample-response.json

One row per prompt per run. Each row is a single line of JSON so the log can be
appended by cron and read back with report.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse import extract, score  # noqa: E402

API = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")


def ask(prompt: str, key: str, max_searches: int) -> dict:
    body = {
        "model": MODEL,
        "max_tokens": 1500,
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": max_searches}],
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code in (429, 529) and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise SystemExit(f"Anthropic API error {err.code}: {err.read().decode()[:300]}")
    raise SystemExit("unreachable")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--out", default="runs.jsonl")
    ap.add_argument("--max-searches", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key and not args.dry_run:
        print("Set ANTHROPIC_API_KEY or use --dry-run", file=sys.stderr)
        return 2

    sample = Path(__file__).parent.parent / "examples" / "sample-response.json"
    today = dt.date.today().isoformat()
    rows = []
    for prompt in cfg["prompts"]:
        response = json.loads(sample.read_text(encoding="utf-8")) if args.dry_run else ask(prompt, key, args.max_searches)
        parsed = extract(response)
        row = {"date": today, "surface": "claude", "prompt": prompt, "searches": parsed["searches"]}
        row.update(score(parsed, cfg["brand"], cfg["competitors"]))
        rows.append(row)
        print(f"{'hit ' if row['mentioned'] else 'miss'}  {prompt}")

    with open(args.out, "a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print(f"{len(rows)} rows appended to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
