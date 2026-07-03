import unittest

from applications.loan_ml.services.data_loader import (
    MAX_UPLOAD_BYTES,
    DatasetValidationError,
    load_csv,
)


class LoadCsvTests(unittest.TestCase):
    def test_loads_valid_csv_and_trims_headers(self):
        result = load_csv(
            "loans.csv",
            b" applicant_income ,loan_status\n5000,Y\n4200,N\n",
        )

        self.assertEqual(result.dataframe.shape, (2, 2))
        self.assertEqual(
            list(result.dataframe.columns),
            ["applicant_income", "loan_status"],
        )
        self.assertEqual(result.metadata["rows"], 2)
        self.assertEqual(result.metadata["columns"], 2)
        self.assertEqual(len(result.fingerprint), 64)

    def test_rejects_non_csv_extension(self):
        with self.assertRaisesRegex(DatasetValidationError, r"\.csv"):
            load_csv("loans.xlsx", b"income,status\n5000,Y\n")

    def test_rejects_empty_file(self):
        with self.assertRaisesRegex(DatasetValidationError, "empty"):
            load_csv("loans.csv", b"")

    def test_rejects_oversized_file(self):
        with self.assertRaisesRegex(DatasetValidationError, "upload limit"):
            load_csv("loans.csv", b"x" * (MAX_UPLOAD_BYTES + 1))

    def test_rejects_header_only_csv(self):
        with self.assertRaisesRegex(DatasetValidationError, "data row"):
            load_csv("loans.csv", b"income,status\n")

    def test_rejects_single_column_csv(self):
        with self.assertRaisesRegex(DatasetValidationError, "at least two columns"):
            load_csv("loans.csv", b"income\n5000\n")

    def test_rejects_missing_header(self):
        with self.assertRaisesRegex(DatasetValidationError, "descriptive header"):
            load_csv("loans.csv", b",status\n5000,Y\n")

    def test_rejects_case_insensitive_duplicate_headers(self):
        with self.assertRaisesRegex(DatasetValidationError, "unique"):
            load_csv("loans.csv", b"Income,income\n5000,4200\n")

    def test_rejects_invalid_utf8(self):
        with self.assertRaisesRegex(DatasetValidationError, "UTF-8"):
            load_csv("loans.csv", b"income,status\n5000,\xff\n")


if __name__ == "__main__":
    unittest.main()
