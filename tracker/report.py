#!/usr/bin/env python3
"""
Turn runs.jsonl into rates, and export the CSV the Java report reads.

    python tracker/report.py runs.jsonl                  # per surface summary
    python tracker/report.py runs.jsonl --by prompt      # one line per prompt
    python tracker/report.py runs.jsonl --by domain      # most cited domains
    python tracker/report.py runs.jsonl --csv out.csv    # for java/VisibilityReport.java

Rows with surface "claude" come from track.py. Rows with surface "ai_overview"
use the same shape. Google has no public AI Overviews API, so those rows come
from whichever SERP data provider you already use. Append them to the same file.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def load(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def rate(n: int, d: int) -> str:
    return f"{n / d:.1%}" if d else "n/a"


def summarize(rows: list[dict], key: str) -> list[tuple]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r.get(key, "all")].append(r)
    out = []
    for name, rs in sorted(groups.items()):
        mention = sum(r["mentioned"] for r in rs)
        cited = sum(r["cited"] for r in rs)
        rival = sum(len(r["competitors"]) for r in rs)
        out.append((name, len(rs), mention, cited, mention / (mention + rival) if mention + rival else None))
    return out


def export_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "surface", "prompt", "mentioned", "cited", "competitors", "cited_domains"])
        for r in rows:
            w.writerow([r["date"], r["surface"], r["prompt"], str(r["mentioned"]).lower(), str(r["cited"]).lower(),
                        "|".join(r["competitors"]), "|".join(r["cited_domains"])])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--by", choices=["surface", "prompt", "date", "domain"], default="surface")
    ap.add_argument("--csv")
    args = ap.parse_args()
    rows = load(args.log)

    if args.csv:
        export_csv(rows, args.csv)
        print(f"wrote {len(rows)} rows to {args.csv}")
        return 0

    if args.by == "domain":
        counts = Counter(d for r in rows for d in r["cited_domains"])
        for d, n in counts.most_common(15):
            print(f"{n:4d}  {d}")
        return 0

    print(f"{args.by:<48} {'runs':>5} {'mention':>8} {'cited':>8} {'SoV':>8}")
    for name, n, m, c, sov in summarize(rows, args.by):
        sov_text = "n/a" if sov is None else f"{sov:.1%}"
        print(f"{name[:48]:<48} {n:>5} {rate(m, n):>8} {rate(c, n):>8} {sov_text:>8}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
