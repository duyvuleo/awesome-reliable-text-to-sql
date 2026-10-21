"""Focused regression checks for publication-blocking validation failures."""

import copy
import tempfile
import unittest
from pathlib import Path

from catalog import canonical_url, public_url_error, recent_papers
from validate import markdown_link_errors, public_content_errors, validate_data


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.paper = {
            "id": "example", "title": "An Example Paper", "year": 2026,
            "publication_status": "preprint", "primary_url": "https://arxiv.org/abs/2601.12345",
            "code_url": None, "dataset_url": None, "topics": ["ambiguity"], "scope": "core",
            "summary": "Studies ambiguous requests. The evaluation has a bounded scope.",
            "evidence": ["https://arxiv.org/abs/2601.12345"], "checked_on": "2026-10-22", "added_on": "2026-10-22",
            "category": "ambiguity", "source_depth": "primary-record",
        }
        self.meta = {"updated": "2026-10-22", "search_cutoff": "2026-10-22", "owner": "example", "repo": "example", "title": "Example"}

    def validate(self, papers=None, resources=None):
        return validate_data(papers if papers is not None else [self.paper], resources or [], self.meta)

    def test_valid_minimal_catalog(self):
        self.assertEqual([], self.validate())

    def test_duplicate_ids_titles_and_arxiv_versions_are_rejected(self):
        second = copy.deepcopy(self.paper)
        second["primary_url"] = "https://arxiv.org/pdf/2601.12345v2.pdf"
        errors = self.validate([self.paper, second])
        for phrase in ("duplicate ID", "duplicate title", "duplicate canonical URL"):
            self.assertTrue(any(phrase in error for error in errors), errors)

    def test_date_uses_meta_not_host_clock(self):
        self.paper["checked_on"] = "2026-10-23"
        self.assertTrue(any("later than meta.updated" in error for error in self.validate()))

    def test_invalid_date_is_rejected(self):
        self.paper["checked_on"] = "2026-02-30"
        self.assertTrue(any("required ISO date" in error for error in self.validate()))

    def test_missing_resource_reference_is_rejected(self):
        resource = {"id": "resource", "name": "Resource", "kind": "dataset", "paper_ids": ["absent"],
                    "url": "https://example.org/data", "description": "Description", "protocol": "Evaluation",
                    "availability": "Public", "license_note": "Unconfirmed", "evidence": ["https://example.org/data"],
                    "checked_on": "2026-10-22"}
        self.assertTrue(any("unknown paper ID" in error for error in self.validate(resources=[resource])))

    def test_private_and_credential_urls_are_rejected(self):
        for host in ("local" + "host", "127.0.0.1", "10.0.0.1", "example.internal", "example.oraclecorp.com"):
            self.assertIsNotNone(public_url_error("https://" + host + "/resource"))
        self.assertIsNotNone(public_url_error("https://" + "user:password@" + "example.org"))

    def test_local_path_and_internal_link_scan(self):
        path = "/" + "Users" + "/" + "example" + "/notes.md"
        internal = "https://" + "example.internal" + "/docs"
        self.assertEqual(2, len(public_content_errors(path + "\n" + internal, "example.md")))

    def test_arxiv_revisions_share_canonical_identity(self):
        self.assertEqual(canonical_url("https://arxiv.org/abs/2601.12345"), canonical_url("https://arxiv.org/pdf/2601.12345v3.pdf"))

    def test_openreview_identifiers_remain_distinct(self):
        self.assertNotEqual(canonical_url("https://openreview.net/forum?id=paper-a"), canonical_url("https://openreview.net/forum?id=paper-b"))

    def test_tracking_parameters_do_not_change_canonical_identity(self):
        self.assertEqual(canonical_url("https://openreview.net/forum?id=paper-a"),
                         canonical_url("https://openreview.net/forum?utm_source=list&id=paper-a&fbclid=tracking#discussion"))

    def test_addition_date_is_required_and_not_after_check_date(self):
        self.paper.pop("added_on")
        self.assertTrue(any("added_on: required ISO date" in error for error in self.validate()))
        self.paper["added_on"] = "2026-10-22"
        self.paper["checked_on"] = "2026-10-21"
        self.assertTrue(any("added_on: later than checked_on" in error for error in self.validate()))

    def test_newly_added_old_paper_precedes_older_addition(self):
        older_work = copy.deepcopy(self.paper)
        older_work.update({"id": "older-work", "year": 2020, "added_on": "2026-10-22"})
        self.paper["added_on"] = "2026-10-21"
        records = [self.paper, older_work]
        before = copy.deepcopy(records)
        self.assertEqual("older-work", recent_papers(records)[0]["id"])
        self.assertEqual(before, records)

    def test_local_links_anchors_and_escape_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "README.md"
            page.write_text('# Overview\n<a id="known"></a>\n', encoding="utf-8")
            valid = "[ok](README.md#known) [heading](#overview)"
            self.assertEqual([], markdown_link_errors(root, page, valid))
            invalid = "[missing](README.md#absent) [escape](../outside.md) [file](missing.md)"
            self.assertEqual(3, len(markdown_link_errors(root, page, invalid)))


if __name__ == "__main__":
    unittest.main()
