import unittest

from scripts.scd_type2 import (
    build_current_history_record,
    build_expired_history_record,
    generate_record_hash,
    has_record_changed,
    is_current_record,
    normalize_hash_value,
)


TRACKED_COLUMNS = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "city",
    "state",
    "source_system",
]


class TestSCDType2(unittest.TestCase):

    def test_normalize_hash_value_handles_nulls_and_blanks(self):
        self.assertEqual(normalize_hash_value(None), "__NULL__")
        self.assertEqual(normalize_hash_value(""), "__NULL__")
        self.assertEqual(normalize_hash_value("   "), "__NULL__")
        self.assertEqual(normalize_hash_value(" Rohith "), "Rohith")

    def test_generate_record_hash_is_stable_for_same_values(self):
        record = {
            "first_name": "Rohith",
            "last_name": "S",
            "email": "rohith@example.com",
            "phone": "9876543210",
            "city": "Bengaluru",
            "state": "Karnataka",
            "source_system": "CSV",
        }

        first_hash = generate_record_hash(record, TRACKED_COLUMNS)
        second_hash = generate_record_hash(record, TRACKED_COLUMNS)

        self.assertEqual(first_hash, second_hash)

    def test_generate_record_hash_changes_when_tracked_column_changes(self):
        old_record = {
            "first_name": "Rohith",
            "last_name": "S",
            "email": "rohith@example.com",
            "phone": "9876543210",
            "city": "Bengaluru",
            "state": "Karnataka",
            "source_system": "CSV",
        }

        new_record = dict(old_record)
        new_record["city"] = "Bangalore"

        self.assertNotEqual(
            generate_record_hash(old_record, TRACKED_COLUMNS),
            generate_record_hash(new_record, TRACKED_COLUMNS),
        )

    def test_build_current_history_record_marks_record_current(self):
        record = {
            "customer_id": "CUST001",
            "first_name": "Rohith",
            "last_name": "S",
            "email": "rohith@example.com",
            "phone": "9876543210",
            "city": "Bengaluru",
            "state": "Karnataka",
            "source_system": "CSV",
        }

        history_record = build_current_history_record(
            record=record,
            tracked_columns=TRACKED_COLUMNS,
            effective_start_date="2026-06-16",
        )

        self.assertTrue(is_current_record(history_record))
        self.assertIsNone(history_record["effective_end_date"])
        self.assertIn("record_hash", history_record)
        self.assertIn("created_at", history_record)
        self.assertIn("updated_at", history_record)

    def test_has_record_changed_detects_changed_record(self):
        current_record = {
            "customer_id": "CUST001",
            "first_name": "Rohith",
            "last_name": "S",
            "email": "rohith@example.com",
            "phone": "9876543210",
            "city": "Bengaluru",
            "state": "Karnataka",
            "source_system": "CSV",
        }

        current_record["record_hash"] = generate_record_hash(
            current_record,
            TRACKED_COLUMNS,
        )

        changed_source_record = dict(current_record)
        changed_source_record["email"] = "rohith.v12@example.com"

        self.assertTrue(
            has_record_changed(
                changed_source_record,
                current_record,
                TRACKED_COLUMNS,
            )
        )

    def test_build_expired_history_record_marks_record_not_current(self):
        current_record = {
            "customer_id": "CUST001",
            "is_current": True,
            "effective_end_date": None,
        }

        expired_record = build_expired_history_record(
            record=current_record,
            effective_end_date="2026-06-18",
        )

        self.assertFalse(expired_record["is_current"])
        self.assertEqual(expired_record["effective_end_date"], "2026-06-18")
        self.assertIn("updated_at", expired_record)


if __name__ == "__main__":
    unittest.main()
