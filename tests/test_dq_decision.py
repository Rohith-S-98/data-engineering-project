import unittest
from scripts.dq_decision import evaluate_dq_status


class TestDQDecision(unittest.TestCase):

    def test_returns_failed_when_high_severity_fails(self):
        rules = [
            {"severity": "HIGH", "failed_count": 1},
            {"severity": "LOW", "failed_count": 0},
        ]

        result = evaluate_dq_status(rules)

        self.assertEqual(result, "FAILED")

    def test_returns_warning_when_medium_or_low_fails(self):
        rules = [
            {"severity": "LOW", "failed_count": 2},
            {"severity": "MEDIUM", "failed_count": 1},
        ]

        result = evaluate_dq_status(rules)

        self.assertEqual(result, "SUCCESS_WITH_WARNINGS")

    def test_returns_success_when_no_failures(self):
        rules = [
            {"severity": "HIGH", "failed_count": 0},
            {"severity": "LOW", "failed_count": 0},
        ]

        result = evaluate_dq_status(rules)

        self.assertEqual(result, "SUCCESS")


if __name__ == "__main__":
    unittest.main()