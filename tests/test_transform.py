"""Tests for transform.py."""

import pandas as pd
import pytest

from ons_mental_health.transform import (
    count_column_names,
    get_unique_column_names,
    normalise_name,
    normalise_column_names,
)


@pytest.fixture
def df_dict():
    """Three small tables with overlapping column names, like the ONS tables."""
    return {
        "Table_1": pd.DataFrame(columns=["Breakdown", "Estimate (%)", "Sample size"]),
        "Table_2": pd.DataFrame(columns=["Breakdown", "Estimate (%)"]),
        "Table_3": pd.DataFrame(columns=["Breakdown", "Notes"]),
    }


def side_by_side(result, expected, gap=6):
    """Return result and expected as text, laid out next to each other."""
    left = ["RESULT", *str(result).splitlines()]
    right = ["EXPECTED", *str(expected).splitlines()]
    width = max(len(line) for line in left) + gap
    rows = max(len(left), len(right))
    left += [""] * (rows - len(left))
    right += [""] * (rows - len(right))
    return "\n".join(f"{a:<{width}}{b}" for a, b in zip(left, right))


def assert_frame_equal_and_show(result, expected):
    """Print result and expected side by side, then compare them.

    pytest shows the printout when the test fails, or for every test
    when run with ``-rP``.
    """
    print("\n" + side_by_side(result, expected) + "\n")
    pd.testing.assert_frame_equal(result, expected)


# --- normalise_name -------------------------------------------------------


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
def test_normalise_name(name, expected):
    assert normalise_name(name) == expected


# --- normalise_column_names ------------------------------------------------------


@pytest.fixture
def table():
    """One small table with un-normalised column names and some data."""
    return pd.DataFrame(
        {
            "Breakdown": ["Male", "Female"],
            "Estimate (%)": [20, 25],
            "Sample size": [2280, 2320],
        }
    )


def test_normalise_column_names_renames_columns_and_keeps_data(table):
    expected = pd.DataFrame(
        {
            "breakdown": ["Male", "Female"],
            "estimate_(%)": [20, 25],
            "sample_size": [2280, 2320],
        }
    )

    result = normalise_column_names(table)

    assert_frame_equal_and_show(result, expected)


def test_normalise_column_names_does_not_modify_input(table):
    normalise_column_names(table)

    assert list(table.columns) == ["Breakdown", "Estimate (%)", "Sample size"]


def test_normalise_column_names_raises_if_two_columns_get_the_same_name():
    clashing = pd.DataFrame(columns=["Sample size", "sample_size"])

    with pytest.raises(ValueError):
        normalise_column_names(clashing)


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
