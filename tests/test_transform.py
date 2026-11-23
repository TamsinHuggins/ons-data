"""Tests for transform.py."""

import pandas as pd
import pytest

from ons_mental_health.transform import (
    add_source_column,
    count_column_names,
    normalise_name,
    normalise_column_names,
    union_tables,
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


# --- add_source_column ----------------------------------------------------


def test_add_source_column_adds_table_name_as_first_column(table):
    expected = pd.DataFrame(
        {
            "source_table": ["Table_4", "Table_4"],
            "Breakdown": ["Male", "Female"],
            "Estimate (%)": [20, 25],
            "Sample size": [2280, 2320],
        }
    )

    result = add_source_column(table, "Table_4")

    assert_frame_equal_and_show(result, expected)


def test_add_source_column_does_not_modify_input(table):
    add_source_column(table, "Table_4")

    assert "source_table" not in table.columns


def test_add_source_column_raises_if_source_column_already_exists(table):
    already_has_source = add_source_column(table, "Table_4")

    with pytest.raises(ValueError):
        add_source_column(already_has_source, "Table_5")


# --- union_tables ---------------------------------------------------------


@pytest.fixture
def tables_with_data():
    """Two small tables with data. Only Table_2 has a Notes column."""
    return {
        "Table_1": pd.DataFrame(
            {
                "Breakdown": ["Male", "Female"],
                "Estimate (%)": [20, 25],
            }
        ),
        "Table_2": pd.DataFrame(
            {
                "Breakdown": ["All"],
                "Estimate (%)": [18],
                "Notes": ["[note 4]"],
            }
        ),
    }


def test_union_tables_stacks_tables_with_nan_for_missing_columns(tables_with_data):
    expected = pd.DataFrame(
        {
            "source_table": ["Table_1", "Table_1", "Table_2"],
            "breakdown": ["Male", "Female", "All"],
            "estimate_(%)": [20, 25, 18],
            "notes": [None, None, "[note 4]"],
        }
    )

    result = union_tables(tables_with_data)

    assert_frame_equal_and_show(result, expected)


def test_union_tables_has_fresh_index(tables_with_data):
    result = union_tables(tables_with_data)

    assert list(result.index) == [0, 1, 2]


def test_union_tables_matches_columns_differing_by_case_or_spaces():
    tables = {
        "Table_1": pd.DataFrame({"Sample size": [100]}),
        "Table_2": pd.DataFrame({"sample_size": [200]}),
    }

    result = union_tables(tables)

    assert list(result.columns) == ["source_table", "sample_size"]
    assert list(result["sample_size"]) == [100, 200]


def test_union_tables_does_not_modify_input(tables_with_data):
    union_tables(tables_with_data)

    assert list(tables_with_data["Table_1"].columns) == ["Breakdown", "Estimate (%)"]


def test_union_tables_raises_if_columns_in_one_table_clash():
    tables = {"Table_1": pd.DataFrame(columns=["Sample size", "sample_size"])}

    with pytest.raises(ValueError):
        union_tables(tables)


def test_union_tables_raises_if_there_are_no_tables():
    with pytest.raises(ValueError, match="No tables"):
        union_tables({})
