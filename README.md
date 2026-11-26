# Best Claude SEO Tracking Tools

<p align="center">
  <a href="https://aiclicks.io/">
    <img src="REPLACE_WITH_SCREENSHOT_URL" alt="best-claude-seo-tracking-tools" />
  </a>
</p>

Claude has no rank. There is no position 3 to watch, no results page to scrape, and the same question can return a different shortlist an hour later. What can be measured is the answer itself: whether a brand is named, whether its URL is cited, and which competitors share the paragraph. That is the job of the [best claude seo tracking tools](https://aiclicks.io/blog/best-claude-seo-tracking-tools), and it is closer to log analysis than to classic rank checking.

This repo takes that literally. It has two halves. The first is a dataset of eight trackers in [tools.yaml](tools.yaml), rendered into the table below by [render_table.py](render_table.py), with the engine count and the cost per prompt computed instead of typed. The second is working code. A Python tracker in [tracker/](tracker/) sends your own prompts to the Claude Messages API with the web search tool switched on and logs every answer. A Java class in [java/](java/) reads that log and reports mention rate, citation rate and share of voice per surface. If you are comparing [seo tracking software](https://aiclicks.io/trackers/claude-ai-tracker) for Claude, running these on a few dozen prompts is a fair way to test any vendor's numbers before paying.

```
.
├── tools.yaml                   eight trackers, one entry each
├── render_table.py              tools.yaml -> README table, --check, --budget, --need-aio
├── tracker/
│   ├── track.py                 prompts -> POST /v1/messages (web_search tool) -> runs.jsonl
│   ├── parse.py                 pure helpers: text, citations, mentions, domains
│   ├── report.py                runs.jsonl -> summary views, --csv export
│   └── prompts.example.json     brand, aliases, domains, competitors, prompts
├── java/VisibilityReport.java   CSV -> mention rate, citation rate, share of voice per surface
├── examples/
│   ├── sample-response.json     Messages API shape the parser is tested against
│   ├── make_sample_runs.py      builds the synthetic log below (fixed seed)
│   ├── sample-runs.jsonl        40 synthetic rows, fictional brands
│   └── sample-runs.csv          the same rows as CSV for the Java report
├── tests/test_tracker.py        unittest, no network, no API key
└── .github/workflows/checks.yml table check, Python tests, Java build, link check
```

## What a Claude tracker actually measures

Claude answers from two places. Its training data covers what it already knows about a category, and the web search tool, when it is enabled, pulls live pages into the answer. Only the second source can be influenced this month, which is why a tracker that cannot show you the cited URLs is mostly a mention counter.

Three numbers matter, and the code below computes all of them:

- **Mention rate** is the share of runs where the brand name appears in the answer text.
- **Citation rate** is the share of runs where one of the brand's own URLs appears as a citation on the answer.
- **Share of voice** is brand mentions divided by brand plus competitor mentions across the same prompts.

A mention without a citation means Claude knows the name but did not send anyone to the site. A citation without a mention is rarer and usually means a product page was used as a source for someone else's recommendation. Both are worth separating, and a tool that reports one blended score hides the difference.

## Comparison

The table covers the Claude and Google AI Overviews columns that decide most purchases. Entry prices are the plan each vendor lists first, collected in November 2026, in the currency the vendor publishes. Confirm on the vendor's own page before buying.

<!-- TABLE:START -->
| Tool | Entry price | Claude | AI Overviews | Engines named | Per prompt | Trial | Best for |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [AIclicks](https://aiclicks.io/trackers/claude-ai-tracker) | $59/mo, Starter | Yes | Yes | 9 | $1.97/prompt | 3 days | Teams that want citations by URL plus a fix list and GA4 referral data |
| [XSeek](https://www.xseek.io/en) | $99.99/mo, Visibility | Yes | Not named | 9 | $10/prompt | Not stated | Real time alerts and page level Claude citations |
| [LPagery Claude AI Rank Tracker](https://lpagery.io/) | $59/mo, Starter | Yes | Not named | 3 | Not stated | 7 days | Small brands that want simple weekly reports and local prompt variants |
| [LLMrefs](https://llmrefs.com/) | $79/mo, Pro | Yes | Not named | 8 | $0.16/prompt | Free plan, 1 keyword | One blended visibility score across many engines, with CSV export |
| [Orchly](http://orchly.ai/) | $49/mo, Essential | Yes | Yes | 6 | Not stated | Not stated | Multi site teams that want AI citations next to backlink and rank data |
| [Rankability](https://www.rankability.com/) | $199/mo, Core | Yes | Yes | 8 | Not stated | Not stated | Agencies that need white label reports and citation pattern analysis |
| [AI Rank Lab](https://www.airanklab.com/) | $69/mo, Starter | Yes | Not named | 4 | Not stated | Free plan | Startups that want a free way in before paying |
| [Keyword.com](http://keyword.com/) | $24.50/mo, 50 credits | Yes | Yes | 7 | Not stated | 14 days | Classic SERP rank tracking teams adding AI surfaces, with API and Looker Studio |
<!-- TABLE:END -->

Reading it takes three steps. Every tool names Claude on its entry plan, so Claude coverage alone does not separate them. Only four name AI Overviews, which matters if the goal is one tool for both surfaces. And five of the eight do not publish a prompt limit on the entry plan, so a cost per prompt cannot be worked out without asking sales.

To filter the same dataset from the command line:

```bash
pip install pyyaml
python render_table.py --need-aio      # tools that also name Google AI Overviews
python render_table.py --budget 100    # entry plans at or under 100 a month
python render_table.py --check         # exits 1 if the README table drifted from tools.yaml
```

## Choosing without reading eight pricing pages

Most teams need one tracker and one habit, not all eight.

**A small team that wants the cheapest way to start** should look at the free or low entry plans first. AI Rank Lab has a free plan and LLMrefs has a free plan limited to one keyword. Both are enough to find out whether Claude mentions the brand at all.

**An in house SEO team that already pays for a classic rank tracker** should try the AI add on from that vendor before buying a second platform. Keyword.com is the example here, with the lowest entry price in the table and API and Looker Studio support. The trade off is that its AI diagnostics are shallower than a dedicated tracker.

**An agency** needs white label reports and many sites under one login. Rankability and AI Rank Lab list white label reporting, and Orchly targets multi site setups.

**A team that wants a fix list as well as a score** should favour the tools that attach recommendations to each gap. AIclicks lists recommendations and XSeek ships a content studio. On the entry plans the gap is large, since XSeek works out at about $10 per prompt against $1.97 for AIclicks.

Two questions settle most close calls. Does the entry plan include the engines you actually care about, or only the first few? And can you export the raw answers, so that a number on a dashboard can be checked against the text that produced it?

## Run the tracker

The tracker uses only the Python standard library and needs Python 3.9 or newer.

```bash
export ANTHROPIC_API_KEY=your_key_here
python tracker/track.py tracker/prompts.example.json
python tracker/report.py runs.jsonl
```

`track.py` sends each prompt to `POST https://api.anthropic.com/v1/messages` with the web search tool attached:

```python
body = {
    "model": MODEL,                      # CLAUDE_MODEL env var, default claude-sonnet-5-5
    "max_tokens": 1500,
    "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
    "messages": [{"role": "user", "content": prompt}],
}
headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
```

The parser in [tracker/parse.py](tracker/parse.py) reads three block types from the response. `text` blocks carry the answer and their `citations`. `server_tool_use` blocks count the searches Claude ran. `web_search_tool_result` blocks list everything it retrieved, including pages it read but never cited, which is useful for finding sources worth earning a place on.

Edit [tracker/prompts.example.json](tracker/prompts.example.json) with your brand name, its aliases, your domains and your competitors. Keep the prompts commercial, such as "best seo tracking software for a small team". A definitional prompt returns a definition and no shortlist, so there is nothing to measure.

Try it with no key and no network:

```bash
python tracker/track.py tracker/prompts.example.json --dry-run --out /tmp/runs.jsonl
python -m unittest discover -s tests
```

### Reading the log

```bash
python tracker/report.py examples/sample-runs.jsonl
```

```
surface                                           runs  mention    cited      SoV
ai_overview                                         20    25.0%     5.0%    14.7%
claude                                              20    40.0%    35.0%    20.5%
```

Those rows are synthetic and use fictional brands, so the numbers only show the shape of the output. Other views are `--by prompt`, `--by date` and `--by domain`, which lists the most cited domains across all answers.

## AI Overviews rows

Google does not publish an API for AI Overviews, so `track.py` does not fetch them. The tracker handles that by treating the surface as a field. Any row with `"surface": "ai_overview"` and the same keys as a Claude row is summarised next to Claude in the same report. Fill those rows from whichever SERP data provider you already use, then append them to `runs.jsonl`. This is also why the table above separates a Claude column from an AI Overviews column. A vendor that covers both is doing the second half through a third party feed, and it is fair to ask which one.

## The Java report

Teams that already run reporting on the JVM can read the same log without Python. Export it once, then compile and run:

```bash
python tracker/report.py examples/sample-runs.jsonl --csv examples/sample-runs.csv
javac -d out java/VisibilityReport.java
java -cp out VisibilityReport examples/sample-runs.csv
```

```
surface         runs   mention     cited       SoV
ai_overview       20     25.0%      5.0%     14.7%
claude            20     40.0%     35.0%     20.5%
```

The class needs Java 17 or newer and nothing else. It parses quoted CSV fields, so prompts that contain commas survive the export, and it computes share of voice with the same formula as the Python report:

```java
double shareOfVoice() {
    int total = mentions + rivalMentions;
    return total == 0 ? 0 : (double) mentions / total;
}
```

## Practical habits

Run the same prompt set on a schedule, because a single answer is a sample and not a fact. Weekly is enough for most categories, and daily only pays off when the category moves fast. Track at least 30 prompts before reading a trend into the numbers, since a swing of one mention in five prompts is noise. Check that `robots.txt` does not block the crawlers that feed these engines, and that key pages render without client side JavaScript, because a page Claude cannot read cannot be cited.

When a competitor is cited and the brand is not, open that URL. The page type usually explains it. Listicles, comparison pages and forum threads are common sources in these answers, so the fix is often a mention on someone else's page and not an edit to your own.

## FAQ

### How do I track a brand in Claude?
Send a fixed set of commercial prompts to Claude with web search enabled on a schedule, then log whether each answer names the brand, cites its domain and names competitors. The code in this repo does that with one API call per prompt.

### What is an AI Overview rank tracker?
An AI Overview rank tracker records whether Google's AI generated summary appears for a query and which sources it cites. It differs from a classic rank tracker because the unit measured is a cited source inside a summary, not a numbered position.

### Is Claude citation tracking the same as SEO tracking software?
No. Classic SEO tracking software records a position for a keyword on a results page. Claude citation tracking records whether a brand appears inside a generated answer, which has no position at all.

### Does Claude always search the web?
No. Claude answers from training data unless the web search tool is enabled for the request. A tracker that does not turn it on is measuring what the model already knows, which changes slowly and cannot be influenced quickly.

## Contributing

Corrections are the most useful contribution, because vendor pricing changes every few months. See [CONTRIBUTING.md](CONTRIBUTING.md). The code and analysis in this repo are original to it. Released under the [MIT License](LICENSE).
