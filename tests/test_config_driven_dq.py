import unittest

from scripts.config_driven_dq import (
    check_not_null,
    check_allowed_values,
    get_duplicate_keys,
    apply_dq_rules,
)


class TestConfigDrivenDQ(unittest.TestCase):

    def test_check_not_null_passes_when_value_exists(self):
        row = {"email": "test@example.com"}

        result = check_not_null(row, "email")

        self.assertTrue(result)

    def test_check_not_null_fails_when_value_is_empty(self):
        row = {"email": ""}

        result = check_not_null(row, "email")

        self.assertFalse(result)

    def test_check_allowed_values_passes_for_valid_value(self):
        row = {"source_system": "CSV"}

        result = check_allowed_values(row, "source_system", ["CSV", "API"])

        self.assertTrue(result)

    def test_check_allowed_values_fails_for_invalid_value(self):
        row = {"source_system": "CRM"}

        result = check_allowed_values(row, "source_system", ["CSV", "API"])

        self.assertFalse(result)

    def test_get_duplicate_keys_returns_duplicate_customer_id(self):
        rows = [
            {"customer_id": "CUST001"},
            {"customer_id": "CUST002"},
            {"customer_id": "CUST002"},
        ]

        result = get_duplicate_keys(rows, "customer_id")

        self.assertEqual(result, {"CUST002"})

    def test_apply_dq_rules_splits_valid_and_quarantine_rows(self):
        rows = [
            {
                "customer_id": "CUST001",
                "email": "rohith@example.com",
                "phone": "9876543210",
                "source_system": "CSV",
            },
            {
                "customer_id": "CUST002",
                "email": "anil@example.com",
                "phone": "9876543211",
                "source_system": "API",
            },
            {
                "customer_id": "CUST002",
                "email": "anil@example.com",
                "phone": "9876543211",
                "source_system": "API",
            },
            {
                "customer_id": "CUST003",
                "email": "",
                "phone": "9876543212",
                "source_system": "CSV",
            },
        ]

        rules_config = {
            "table_name": "customer",
            "primary_key": "customer_id",
            "rules": [
                {
                    "rule_name": "customer_id_not_null",
                    "column": "customer_id",
                    "rule_type": "not_null",
                    "severity": "HIGH",
                },
                {
                    "rule_name": "email_not_null",
                    "column": "email",
                    "rule_type": "not_null",
                    "severity": "HIGH",
                },
                {
                    "rule_name": "phone_not_null",
                    "column": "phone",
                    "rule_type": "not_null",
                    "severity": "MEDIUM",
                },
                {
                    "rule_name": "customer_id_unique",
                    "column": "customer_id",
                    "rule_type": "unique",
                    "severity": "HIGH",
                },
                {
                    "rule_name": "source_system_allowed_values",
                    "column": "source_system",
                    "rule_type": "allowed_values",
                    "allowed_values": ["CSV", "API"],
                    "severity": "LOW",
                },
            ],
        }

        valid_rows, quarantine_rows, rule_results = apply_dq_rules(rows, rules_config)

        self.assertEqual(len(valid_rows), 1)
        self.assertEqual(len(quarantine_rows), 3)
        self.assertEqual(len(rule_results), 20)


if __name__ == "__main__":
    unittest.main()