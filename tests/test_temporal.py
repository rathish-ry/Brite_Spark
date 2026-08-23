import unittest
from src.models import Clause
from src.temporal import (
    TemporalContext,
    extract_temporal_context,
    is_clause_applicable,
    filter_temporally_applicable_clauses,
)


class TestTemporalPolicy(unittest.TestCase):

    def setUp(self):
        # Original Policy Clauses
        self.c_orig_disregard = Clause(
            id="C024", section="6.4 Disregards", heading="6.4 Disregards", text="$120 per month", source_start=10, source_end=15
        )
        self.c_orig_reporting = Clause(
            id="C015", section="4.3 Change of Circumstances", heading="4.3.2 Time limits", text="10 calendar days", source_start=20, source_end=25
        )

        # Amendment Clauses
        self.c_amd_disregard = Clause(
            id="A2026-01-C01",
            section="Section 1: Disregards",
            heading="Paragraph 1.1",
            text="substitute $175 per month",
            source_start=1,
            source_end=5,
            source_file="data/Amendment No. 2026-01.md",
            amendment_id="A2026-01",
            effective_date="2026-03-01",
            applicability_type="determination",
            target_clause_id="C024",
        )
        self.c_amd_reporting = Clause(
            id="A2026-01-C02",
            section="Section 2: Time Limits",
            heading="Paragraph 2.1",
            text="substitute 14 calendar days",
            source_start=6,
            source_end=10,
            source_file="data/Amendment No. 2026-01.md",
            amendment_id="A2026-01",
            effective_date="2026-03-01",
            applicability_type="change_of_circumstance",
            target_clause_id="C015",
        )

        self.all_clauses = [
            self.c_orig_disregard,
            self.c_orig_reporting,
            self.c_amd_disregard,
            self.c_amd_reporting,
        ]

    def test_determination_date_pre_march(self):
        # Determination on 28 February 2026 -> original rule ($120) applies, amendment ($175) excluded
        ctx = extract_temporal_context("What was the earnings disregard for a determination on 28 February 2026?")
        self.assertEqual(ctx.determination_date, "2026-02-28")

        applicable = filter_temporally_applicable_clauses(self.all_clauses, ctx)
        app_ids = [c.id for c in applicable]

        self.assertIn("C024", app_ids)
        self.assertNotIn("A2026-01-C01", app_ids)

    def test_determination_date_post_march(self):
        # Determination on 1 March 2026 -> amended rule ($175) applies, original ($120) superseded
        ctx = extract_temporal_context("What was the earnings disregard for a determination on 1 March 2026?")
        self.assertEqual(ctx.determination_date, "2026-03-01")

        applicable = filter_temporally_applicable_clauses(self.all_clauses, ctx)
        app_ids = [c.id for c in applicable]

        self.assertIn("A2026-01-C01", app_ids)
        self.assertNotIn("C024", app_ids)

    def test_change_date_pre_march(self):
        # Change on 20 February 2026 -> old reporting rule (10 days) applies, amendment (14 days) excluded
        ctx = extract_temporal_context("A change occurred on 20 February 2026. How long to report?")
        self.assertEqual(ctx.change_date, "2026-02-20")

        applicable = filter_temporally_applicable_clauses(self.all_clauses, ctx)
        app_ids = [c.id for c in applicable]

        self.assertIn("C015", app_ids)
        self.assertNotIn("A2026-01-C02", app_ids)

    def test_change_date_post_march(self):
        # Change on 5 March 2026 -> amended reporting rule (14 days) applies, old rule (10 days) superseded
        ctx = extract_temporal_context("A change occurred on 5 March 2026. How long to report?")
        self.assertEqual(ctx.change_date, "2026-03-05")

        applicable = filter_temporally_applicable_clauses(self.all_clauses, ctx)
        app_ids = [c.id for c in applicable]

        self.assertIn("A2026-01-C02", app_ids)
        self.assertNotIn("C015", app_ids)

    def test_spanning_claim_period(self):
        # Claim spanning 1 March 2026 -> both original and amended clauses remain for apportionment
        ctx = extract_temporal_context("How are figures calculated for a claim period spanning 1 March 2026?")
        self.assertTrue(ctx.is_spanning)

        applicable = filter_temporally_applicable_clauses(self.all_clauses, ctx)
        app_ids = [c.id for c in applicable]

        self.assertIn("C024", app_ids)
        self.assertIn("A2026-01-C01", app_ids)


if __name__ == "__main__":
    unittest.main()
