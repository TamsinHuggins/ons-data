"""Functions for inspecting and reshaping tables loaded from ONS workbooks."""

import pandas as pd


def normalise_column_name(name: str) -> str:
    """Convert a column name to lowercase, with spaces replaced by underscores.

    No other characters are changed, so punctuation such as brackets and
    percent signs is kept.

    Args:
        name: A column name, e.g. ``"Sample size"``.

    Returns:
        The normalised name, e.g. ``"sample_size"``.
    """
    name_lowercase = name.lower()
    names_list = name_lowercase.split(sep=" ")
    clean_column_name = "_".join(names_list)
    return clean_column_name


def count_column_names(df_dict: dict[str, pd.DataFrame]) -> pd.Series:
    """Count how many tables each column name appears in.

    Column names are counted exactly as they appear in the tables, without
    normalising, so inconsistencies between tables remain visible.

    Args:
        df_dict: DataFrames keyed by table name, as returned by
            ``load.get_dfs_from_sheets``.

    Returns:
        Number of tables each column name appears in, indexed by column name
        and sorted from most to least common. Empty if ``df_dict`` is empty.
    """
    raise NotImplementedError


def get_unique_column_names(df_dict: dict[str, pd.DataFrame]) -> list[str]:
    """List the unique column names across all tables, after normalising them.

    Each name is normalised with ``normalise_column_name`` before duplicates
    are removed, so names differing only by capitalisation or spaces versus
    underscores count as the same name. The input tables are not modified.

    Args:
        df_dict: DataFrames keyed by table name, as returned by
            ``load.get_dfs_from_sheets``.

    Returns:
        Unique normalised column names, in the order they first appear when
        reading the tables in order. Empty if ``df_dict`` is empty.
    """
    raise NotImplementedError
