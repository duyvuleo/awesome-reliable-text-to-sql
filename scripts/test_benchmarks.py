"""Guard comparison provenance, explicit unknowns, and resource completeness."""

import copy
import unittest

from catalog import BENCHMARK_FIELDS
from validate import validate_benchmarks


class BenchmarkValidationTests(unittest.TestCase):
    def setUp(self):
        self.resources = [{"id": "example-data", "kind": "dataset"}]
        self.meta = {"updated": "2026-10-22"}
        self.record = {
            "resource_id": "example-data", "label": "Example", "relevance": "direct",
            "ambiguity": {"status": "yes", "detail": "Alternative interpretations."},
            "unanswerability": {"status": "not_reported", "detail": "Not established in the checked task."},
            "clarification": {"mode": "supplied", "detail": "Recorded feedback."},
            "interaction": {"mode": "recorded", "detail": "Offline conversations."},
            "domain": "Example domain", "evaluation": "SQL correctness",
            "data_access": "release_unverified", "checked_on": "2026-10-22",
            "evidence": [{"url": "https://example.org/paper", "locator": "Task and evaluation sections",
                          "supports": sorted(BENCHMARK_FIELDS)}],
        }

    def validate(self, records=None):
        return validate_benchmarks(records if records is not None else [self.record], self.resources, self.meta)

    def test_explicit_unknown_and_unverified_release_are_valid(self):
        before = copy.deepcopy(self.record)
        self.assertEqual([], self.validate())
        self.assertEqual(before, self.record)

    def test_every_dataset_requires_one_comparison(self):
        self.assertTrue(any("missing dataset" in error for error in self.validate([])))
        self.assertTrue(any("duplicate benchmark" in error for error in self.validate([self.record, self.record])))
        self.record["resource_id"] = "missing"
        self.assertTrue(any("must reference a dataset" in error for error in self.validate()))

    def test_each_field_requires_located_public_provenance(self):
        self.record["evidence"][0]["supports"].remove("unanswerability")
        self.assertTrue(any("missing field provenance for unanswerability" in error for error in self.validate()))
        self.record["evidence"][0]["locator"] = ""
        self.record["evidence"][0]["url"] = "https://" + "example.internal/paper"
        errors = self.validate()
        self.assertTrue(any("locator" in error for error in errors))
        self.assertTrue(any("internal host" in error for error in errors))

    def test_booleans_or_invalid_modes_cannot_replace_explicit_states(self):
        self.record["unanswerability"]["status"] = False
        self.record["clarification"]["mode"] = ["generated"]
        errors = self.validate()
        self.assertTrue(any("unanswerability.status" in error for error in errors))
        self.assertTrue(any("clarification.mode" in error for error in errors))

    def test_verification_date_cannot_exceed_catalog_date(self):
        self.record["checked_on"] = "2026-10-23"
        self.assertTrue(any("later than meta.updated" in error for error in self.validate()))


if __name__ == "__main__":
    unittest.main()
