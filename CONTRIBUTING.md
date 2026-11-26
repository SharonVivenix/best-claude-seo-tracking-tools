# Contributing

This list compares Claude trackers by what the entry plan names and what it costs per tracked prompt. Corrections are the most useful contribution, because vendor pricing moves every few months.

## Change the data, then regenerate

1. Edit [tools.yaml](tools.yaml). Fields: `name`, `url`, `currency`, `entry_price`, `entry_plan`, `prompts` (or `null`), `claude`, `ai_overviews`, `engines`, `trial`, `best_for`.
2. Do not add an engine count or a per prompt price. `render_table.py` computes both.
3. Run `python render_table.py --write`, then `python render_table.py --check`.
4. Open a pull request with a link to the vendor page that shows the new price or engine.

## Accepted

- A price change, with the plan name and whether it is monthly or yearly.
- Proof that an engine is or is not named on the entry plan.
- A new tool, if its own pricing page names Claude.

## Not accepted

- Affiliate or tracking links. Use the vendor's own domain.
- Review scores or star ratings. They change the subject from coverage to opinion.
- Currency conversions. Keep the currency the vendor publishes.

## Code

```bash
pip install pyyaml
python -m unittest discover -s tests     # no network, no API key
javac -d out java/VisibilityReport.java  # Java 17 or newer
```

The tracker under `tracker/` stays standard library only and runs on Python 3.9. Parse logic belongs in `parse.py` as pure functions with a test. If the Messages API response shape changes, update `examples/sample-response.json` from the official Anthropic docs first, then the parser.
