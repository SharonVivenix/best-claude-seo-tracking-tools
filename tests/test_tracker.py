import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tracker"))

from parse import cites, domain, extract, mentions, score  # noqa: E402
import report  # noqa: E402

CFG = json.loads((ROOT / "tracker" / "prompts.example.json").read_text(encoding="utf-8"))
RESPONSE = json.loads((ROOT / "examples" / "sample-response.json").read_text(encoding="utf-8"))


class ParseTests(unittest.TestCase):
    def test_extract_reads_text_citations_and_searches(self):
        p = extract(RESPONSE)
        self.assertIn("Acme Metrics", p["text"])
        self.assertEqual(len(p["cited"]), 2)
        self.assertEqual(p["searches"], 1)
        self.assertEqual(len(p["searched"]), 2)

    def test_mentions_is_whole_word(self):
        self.assertTrue(mentions("try Acme Metrics today", ["Acme Metrics"]))
        self.assertFalse(mentions("Acme Metricsville", ["Acme Metrics"]))

    def test_cites_matches_subdomains_but_not_lookalikes(self):
        self.assertTrue(cites(["https://blog.acmemetrics.example/x"], ["acmemetrics.example"]))
        self.assertFalse(cites(["https://notacmemetrics.example/x"], ["acmemetrics.example"]))

    def test_domain_strips_www(self):
        self.assertEqual(domain("https://www.example.com/a"), "example.com")

    def test_score(self):
        s = score(extract(RESPONSE), CFG["brand"], CFG["competitors"])
        self.assertTrue(s["mentioned"])
        self.assertTrue(s["cited"])
        self.assertEqual(s["competitors"], ["Northwind Rank"])


class ReportTests(unittest.TestCase):
    def test_summarize_share_of_voice(self):
        rows = [
            {"surface": "claude", "mentioned": True, "cited": True, "competitors": ["A"]},
            {"surface": "claude", "mentioned": False, "cited": False, "competitors": ["A", "B"]},
        ]
        name, runs, m, c, sov = report.summarize(rows, "surface")[0]
        self.assertEqual((name, runs, m, c), ("claude", 2, 1, 1))
        self.assertAlmostEqual(sov, 0.25)


if __name__ == "__main__":
    unittest.main()
