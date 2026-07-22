"""Regression tests for the delegation design analysis.

These assert the qualitative findings the revision reports, not exact values,
so the checks stay stable under reasonable reps while still failing if a frozen
construct stops being indicted.
"""

from __future__ import annotations

import unittest

import numpy as np

from scripts.design_analysis import (
    local_discrimination,
    predictive_ablation,
    reviewer_reconstruction,
)


class DesignAnalysisTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = np.random.default_rng(20260722)
        self.reps = 4000

    def test_subtract_max_nuisance_biases_low(self) -> None:
        out = local_discrimination(self.reps, self.rng)
        # the maximum of noisy nonnegative nuisances is inflated, so the rule
        # over-subtracts: the estimand is biased below the true effect
        self.assertLess(out["naive_bias_subtract_max_nuisance"], -0.02)
        # modelling the common nuisance mean nearly removes the bias
        self.assertLess(
            abs(out["modelled_bias_subtract_mean_nuisance"]),
            abs(out["naive_bias_subtract_max_nuisance"]),
        )

    def test_gate_exaggerates_passing_estimates(self) -> None:
        out = local_discrimination(self.reps, self.rng)
        # conditioning on a one-sided lower-bound gate inflates the reported
        # effect (Type M): the exaggeration ratio exceeds one
        self.assertGreater(out["type_m_exaggeration_given_gate_modelled"], 1.0)

    def test_ece_gate_false_fails_perfect_calibration(self) -> None:
        out = predictive_ablation(self.reps, self.rng)
        # a perfectly calibrated predictor should not be failed, yet the ten-bin
        # ECE gate at n=30 rejects it most of the time from binning noise alone
        self.assertGreater(out["ece_gate_false_fail_rate_at_0.10"], 0.5)
        self.assertGreater(out["mean_ece_under_perfect_calibration"], 0.10)

    def test_normal_cluster_interval_undercovers(self) -> None:
        out = predictive_ablation(self.reps, self.rng)
        # the z interval over ten clusters undercovers; the t interval is closer
        self.assertLess(out["normal_lcb_coverage"], out["t_interval_coverage"])

    def test_max_of_two_ses_undercovers_vs_crossed(self) -> None:
        out = reviewer_reconstruction(self.reps, self.rng)
        # taking the larger of two one-way cluster SEs ignores a variance
        # component of the crossed design and undercovers
        self.assertLess(out["max_of_two_ses_coverage"], 0.93)
        self.assertGreater(
            out["crossed_known_components_coverage"], out["max_of_two_ses_coverage"]
        )


if __name__ == "__main__":
    unittest.main()
