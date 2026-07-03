import unittest

import pandas as pd

from applications.loan_ml.services.exploration import (
    correlation_matrix,
    dataframe_to_csv,
    detect_target_column,
    missing_value_summary,
    numeric_feature,
    profile_dataset,
    statistical_summary,
    target_distribution,
)
from applications.loan_ml.utils.helpers import format_bytes


class ExplorationServiceTests(unittest.TestCase):
    def setUp(self):
        self.dataframe = pd.DataFrame(
            {
                "ApplicantIncome": [5000, 4200, 5000],
                "LoanAmount": [150.0, None, 150.0],
                "PropertyArea": ["Urban", "Rural", "Urban"],
                "LoanApproved": ["Yes", "No", "Yes"],
            }
        )

    def test_profiles_dataset(self):
        profile = profile_dataset(self.dataframe)

        self.assertEqual(profile.rows, 3)
        self.assertEqual(profile.columns, 4)
        self.assertEqual(profile.missing_values, 1)
        self.assertEqual(profile.duplicate_rows, 1)
        self.assertEqual(
            profile.numeric_columns,
            ("ApplicantIncome", "LoanAmount"),
        )
        self.assertEqual(
            profile.categorical_columns,
            ("PropertyArea", "LoanApproved"),
        )
        self.assertGreater(profile.memory_bytes, 0)

    def test_builds_sorted_missing_value_summary(self):
        summary = missing_value_summary(self.dataframe)

        self.assertEqual(summary.iloc[0]["Column"], "LoanAmount")
        self.assertEqual(summary.iloc[0]["Missing Values"], 1)
        self.assertAlmostEqual(summary.iloc[0]["Missing (%)"], 33.33)

    def test_statistical_summary_can_include_categorical_columns(self):
        numeric_summary = statistical_summary(self.dataframe)
        full_summary = statistical_summary(
            self.dataframe,
            include_categorical=True,
        )

        self.assertEqual(
            list(numeric_summary.index),
            ["ApplicantIncome", "LoanAmount"],
        )
        self.assertIn("PropertyArea", full_summary.index)

    def test_detects_loan_target_case_and_separator_insensitively(self):
        self.assertEqual(
            detect_target_column(self.dataframe),
            "LoanApproved",
        )
        aliased = self.dataframe.rename(columns={"LoanApproved": "loan_status"})
        self.assertEqual(detect_target_column(aliased), "loan_status")

    def test_returns_none_for_ambiguous_semantic_targets(self):
        dataframe = pd.DataFrame(
            {
                "application_status": ["open"],
                "approval_reason": ["income"],
            }
        )

        self.assertIsNone(detect_target_column(dataframe))

    def test_calculates_target_distribution_including_missing(self):
        dataframe = self.dataframe.copy()
        dataframe.loc[1, "LoanApproved"] = None

        distribution = target_distribution(dataframe, "LoanApproved")

        self.assertEqual(distribution["Count"].sum(), len(dataframe))
        self.assertIn("Missing", distribution["Value"].tolist())

    def test_validates_numeric_feature(self):
        values = numeric_feature(self.dataframe, "LoanAmount")
        self.assertEqual(values.tolist(), [150.0, 150.0])

        with self.assertRaises(TypeError):
            numeric_feature(self.dataframe, "PropertyArea")

    def test_calculates_numeric_correlations(self):
        correlations = correlation_matrix(self.dataframe)

        self.assertEqual(
            list(correlations.columns),
            ["ApplicantIncome", "LoanAmount"],
        )
        self.assertEqual(correlations.loc["ApplicantIncome", "ApplicantIncome"], 1)

    def test_serializes_dataframe_without_index(self):
        content = dataframe_to_csv(self.dataframe).decode("utf-8")

        self.assertTrue(content.startswith("ApplicantIncome,LoanAmount"))
        self.assertNotIn(",0,", content)

    def test_formats_memory_size(self):
        self.assertEqual(format_bytes(0), "0 B")
        self.assertEqual(format_bytes(1536), "1.5 KB")


if __name__ == "__main__":
    unittest.main()
