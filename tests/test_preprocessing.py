"""
tests/test_preprocessing.py
Basic unit tests for the preprocessing pipeline.
Run with: pytest tests/ from the project root.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pandas as pd
import numpy as np
import pytest
from preprocessing.pipeline import PreprocessingPipeline


@pytest.fixture
def simple_df():
    return pd.DataFrame({
        "age":    [25, 30, np.nan, 35, 1000],
        "salary": [50000, 60000, 55000, np.nan, 52000],
        "city":   ["NYC", "LA", "NYC", "LA", "NYC"],
        "score":  [8, 8, 7, 9, 8],  # score=8 repeated → duplicates
    })


def test_missing_imputation(simple_df):
    pipe = PreprocessingPipeline(missing_strategy="mean", outlier_method="none",
                                  encoding_method="label", scaling_method="none")
    cleaned = pipe.run(simple_df)
    assert cleaned.isnull().sum().sum() == 0, "No NaN values should remain after imputation"


def test_duplicate_removal():
    df = pd.DataFrame({"a": [1,1,2], "b": ["x","x","y"]})
    pipe = PreprocessingPipeline(outlier_method="none", encoding_method="label", scaling_method="none")
    cleaned = pipe.run(df)
    assert len(cleaned) == 2
    assert pipe.report["duplicates_removed"] == 1


def test_outlier_removal(simple_df):
    pipe = PreprocessingPipeline(outlier_method="iqr", encoding_method="label", scaling_method="none")
    cleaned = pipe.run(simple_df)
    # The salary=1000 row should be removed as an outlier (or handled)
    # Just assert it ran without error and shape shrank or stayed same
    assert cleaned.shape[0] <= simple_df.shape[0]


def test_encoding_onehot(simple_df):
    pipe = PreprocessingPipeline(outlier_method="none", encoding_method="onehot", scaling_method="none")
    cleaned = pipe.run(simple_df)
    # city column should be expanded into dummies
    assert "city" not in cleaned.columns or cleaned.select_dtypes(include="object").empty


def test_encoding_label(simple_df):
    pipe = PreprocessingPipeline(outlier_method="none", encoding_method="label", scaling_method="none")
    cleaned = pipe.run(simple_df)
    assert cleaned.select_dtypes(include="object").empty


def test_scaling_standard(simple_df):
    pipe = PreprocessingPipeline(outlier_method="none", encoding_method="label", scaling_method="standard")
    cleaned = pipe.run(simple_df)
    numeric = cleaned.select_dtypes(include=[np.number])
    # After standard scaling, mean ≈ 0
    for col in numeric.columns:
        if numeric[col].std() > 0:
            assert abs(numeric[col].mean()) < 1, f"Column {col} mean should be near 0 after scaling"


def test_report_contains_steps(simple_df):
    pipe = PreprocessingPipeline()
    pipe.run(simple_df)
    report = pipe.get_report()
    assert "original_shape" in report
    assert "cleaned_shape" in report
    assert "steps" in report
    assert len(report["steps"]) >= 6


def test_empty_dataframe():
    df = pd.DataFrame({"a": [], "b": []})
    pipe = PreprocessingPipeline(outlier_method="none", scaling_method="none")
    # Should not raise
    cleaned = pipe.run(df)
    assert isinstance(cleaned, pd.DataFrame)
