"""Tests for transform.py."""

import pandas as pd
import pytest

from ons_mental_health.transform import (
    count_column_names,
    get_unique_column_names,
    normalise_column_name,
)


@pytest.fixture
def df_dict():
    """Three small tables with overlapping column names, like the ONS tables."""
    return {
        "Table_1": pd.DataFrame(columns=["Breakdown", "Estimate (%)", "Sample size"]),
        "Table_2": pd.DataFrame(columns=["Breakdown", "Estimate (%)"]),
        "Table_3": pd.DataFrame(columns=["Breakdown", "Notes"]),
    }


# --- normalise_column_name ------------------------------------------------


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Breakdown", "breakdown"),
        ("Sample size", "sample_size"),
        ("Breakdown category", "breakdown_category"),
        ("Estimate (%)", "estimate_(%)"),
        ("LCL", "lcl"),
        ("already_clean", "already_clean"),
    ],
)
def test_normalise_column_name(name, expected):
    assert normalise_column_name(name) == expected


# --- count_column_names ---------------------------------------------------


def test_count_column_names_returns_a_series(df_dict):
    result = count_column_names(df_dict)

    assert isinstance(result, pd.Series)


def test_count_column_names_counts_tables_each_name_appears_in(df_dict):
    result = count_column_names(df_dict)

    assert result.to_dict() == {
        "Breakdown": 3,
        "Estimate (%)": 2,
        "Sample size": 1,
        "Notes": 1,
    }


def test_count_column_names_is_sorted_most_common_first(df_dict):
    result = count_column_names(df_dict)

    assert list(result.index[:2]) == ["Breakdown", "Estimate (%)"]


def test_count_column_names_keeps_original_names(df_dict):
    df_dict["Table_3"] = pd.DataFrame(columns=["breakdown"])

    result = count_column_names(df_dict)

    assert result["Breakdown"] == 2
    assert result["breakdown"] == 1


def test_count_column_names_empty_dict_returns_empty_series():
    result = count_column_names({})

    assert result.empty


# --- get_unique_column_names ----------------------------------------------


def test_get_unique_column_names_returns_normalised_names_in_first_seen_order(
    df_dict,
):
    result = get_unique_column_names(df_dict)

    assert result == ["breakdown", "estimate_(%)", "sample_size", "notes"]


def test_get_unique_column_names_merges_case_and_spacing_variants():
    df_dict = {
        "Table_1": pd.DataFrame(columns=["Sample size"]),
        "Table_2": pd.DataFrame(columns=["sample size"]),
        "Table_3": pd.DataFrame(columns=["Sample_size"]),
    }

    result = get_unique_column_names(df_dict)

    assert result == ["sample_size"]


def test_get_unique_column_names_empty_dict_returns_empty_list():
    result = get_unique_column_names({})

    assert result == []


def test_get_unique_column_names_does_not_modify_input_tables(df_dict):
    get_unique_column_names(df_dict)

    assert list(df_dict["Table_1"].columns) == [
        "Breakdown",
        "Estimate (%)",
        "Sample size",
    ]
