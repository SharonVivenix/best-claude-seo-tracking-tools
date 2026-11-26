#!/usr/bin/env python3
"""Generate examples/sample-runs.jsonl and sample-runs.csv. Synthetic data, fictional brands, fixed seed."""
import json
import random
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent
random.seed(7)
prompts = json.loads((here.parent / "tracker" / "prompts.example.json").read_text(encoding="utf-8"))["prompts"]
rivals = ["Northwind Rank", "Contoso Tracker", "Fabrikam SERP"]
# Brand mention odds per surface: the made up brand does better in Claude than in AI Overviews.
odds = {"claude": 0.55, "ai_overview": 0.30}

rows = []
for week in range(4):
    for surface, p in odds.items():
        for prompt in prompts:
            mentioned = random.random() < p
            cited = mentioned and random.random() < 0.6
            comp = [r for r in rivals if random.random() < 0.45]
            domains = sorted({"acmemetrics.example"} if cited else set()) + random.sample(
                ["northwind.example", "contoso.example", "reddit.com", "g2.com"], k=2)
            rows.append({"date": f"2026-11-{2 + week * 7:02d}", "surface": surface, "prompt": prompt,
                         "searches": 2, "mentioned": mentioned, "cited": cited,
                         "competitors": comp, "cited_domains": sorted(domains)})

out = here / "sample-runs.jsonl"
out.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
subprocess.check_call([sys.executable, str(here.parent / "tracker" / "report.py"), str(out), "--csv", str(here / "sample-runs.csv")])
