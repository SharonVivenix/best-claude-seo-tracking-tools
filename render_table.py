#!/usr/bin/env python3
"""
Regenerate the comparison table in README.md from tools.yaml.

    python render_table.py                 # print the table to stdout
    python render_table.py --write         # rewrite the block between the markers
    python render_table.py --check         # exit 1 if README and YAML disagree
    python render_table.py --need-aio      # only tools that also name AI Overviews
    python render_table.py --budget 100    # only tools whose entry plan fits a budget

Two columns are computed and never typed: the engine count, and the cost per
tracked prompt where the vendor publishes a prompt limit.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

START = "<!-- TABLE:START -->"
END = "<!-- TABLE:END -->"
HEADER = ["Tool", "Entry price", "Claude", "AI Overviews", "Engines named", "Per prompt", "Trial", "Best for"]


def money(currency: str, value: float) -> str:
    text = f"{value:,.2f}"
    return currency + (text[:-3] if text.endswith(".00") else text)


def per_prompt(t: dict) -> str:
    if not t.get("prompts"):
        return "Not stated"
    return money(t["currency"], round(t["entry_price"] / t["prompts"], 2)) + "/prompt"


def row(t: dict) -> list[str]:
    return [
        f"[{t['name']}]({t['url']})",
        f"{money(t['currency'], t['entry_price'])}/mo, {t['entry_plan']}",
        "Yes" if t["claude"] else "No",
        "Yes" if t["ai_overviews"] else "Not named",
        str(len(t["engines"])),
        per_prompt(t),
        t["trial"],
        t["best_for"],
    ]


def build_table(tools: list[dict]) -> str:
    lines = ["| " + " | ".join(HEADER) + " |", "| " + " | ".join("---" for _ in HEADER) + " |"]
    lines += ["| " + " | ".join(row(t)) + " |" for t in tools]
    return "\n".join(lines)


def load(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--need-aio", action="store_true")
    ap.add_argument("--budget", type=float)
    args = ap.parse_args()

    here = Path(__file__).parent
    tools = load(here / "tools.yaml")
    shown = tools
    if args.need_aio:
        shown = [t for t in shown if t["ai_overviews"]]
    if args.budget is not None:
        shown = [t for t in shown if t["entry_price"] <= args.budget]
    # Filters only change what is printed. --write and --check always use the full list.
    table = build_table(tools if (args.write or args.check) else shown)

    readme = here / "README.md"
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        if args.write or args.check:
            print("README.md is missing the TABLE markers", file=sys.stderr)
            return 1
        print(table)
        return 0

    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{table}\n{END}{tail}"
    if args.write:
        readme.write_text(new, encoding="utf-8")
        return 0
    if args.check:
        if new != text:
            print("README table is out of date. Run: python render_table.py --write", file=sys.stderr)
            return 1
        return 0
    print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
