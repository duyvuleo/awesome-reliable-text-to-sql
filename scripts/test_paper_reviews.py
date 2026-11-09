"""Protect the distinction between retrieval, partial reading and full review."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from paper_reviews import render_reviews, validate_reviews


class ReadingRecordTests(unittest.TestCase):
    def setUp(self):
        self.paper = {"id": "example", "title": "An example", "year": 2026,
                      "source_depth": "full-text-reviewed"}
        self.review = {"paper_id": "example", "status": "full-text-reviewed",
                       "reviewed_on": "2026-11-09", "source_url": "https://example.org/paper.pdf",
                       "version": "Published version", "coverage": "Sections 1-6 and Appendix A",
                       "unread": [], "problem": "Question", "method": "Method",
                       "evaluation": "Protocol", "findings": "Finding", "limitations": "Limit",
                       "relevance": "Relevance", "claims": [{"claim": "A | B", "evidence": "Evidence",
                       "locator": "Table 2", "disposition": "Conditional support"}]}

    def check(self, records=None, paper=None):
        return validate_reviews(records if records is not None else [self.review],
                                [paper or self.paper], "2026-11-09")

    def test_complete_reading_requires_no_unread_material(self):
        self.assertEqual([], self.check())
        self.review["unread"] = ["Appendix A"]
        self.assertTrue(any("cannot have unread" in e for e in self.check()))

    def test_access_failure_cannot_upgrade_catalog_depth(self):
        self.review.update(status="unavailable", unread=["Publisher requires access"], claims=[])
        self.assertTrue(any("needs a completed" in e for e in self.check()))
        paper = dict(self.paper, source_depth="primary-record")
        self.assertEqual([], self.check(paper=paper))

    def test_review_needs_located_evidence_and_unique_identity(self):
        self.review["claims"][0].pop("locator")
        self.assertTrue(any("incomplete claim" in e for e in self.check()))
        self.assertTrue(any("duplicate" in e for e in self.check([self.review, copy.deepcopy(self.review)])))

    def test_depth_cannot_be_upgraded_without_a_record(self):
        self.assertTrue(any("needs a completed" in e for e in self.check([])))

    def test_public_records_reject_internal_fields_and_local_supplements(self):
        self.review["proposed_paper_changes"] = {"summary": "Unreviewed proposal"}
        self.assertTrue(any("unexpected fields" in e for e in self.check()))
        self.review.pop("proposed_paper_changes")
        self.review["additional_sources"] = [{"label": "Supplement", "url": str(Path(tempfile.gettempdir()) / "example-paper.pdf")}]
        self.assertTrue(any("labeled public sources" in e for e in self.check()))
        self.review["additional_sources"][0]["url"] = "https://example.org/supplement.pdf"
        self.assertEqual([], self.check())

    def test_render_preserves_gaps_and_escapes_claim_table(self):
        self.review.update(status="partial", unread=["Supplement not retrieved"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data/paper-reviews.json").write_text(json.dumps([self.review]))
            files = render_reviews(root, [self.paper])
        note = files[Path("papers/notes/example.md")]
        self.assertIn("Supplement not retrieved", note)
        self.assertIn("A &#124; B", note)
        self.assertIn("**0 full-paper readings**", files[Path("papers/reading-notes.md")])


if __name__ == "__main__":
    unittest.main()
