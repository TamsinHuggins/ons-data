"""Functions for inspecting and reshaping tables loaded from ONS workbooks."""

from collections import Counter

import pandas as pd


def normalise_name(name: str) -> str:
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


def normalise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of a DataFrame with every column name normalised.

    Each column name is converted with ``normalise_name``. Data values, row
    order and the index are unchanged, and the input DataFrame is not modified.

    Args:
        df: A table whose column names should be normalised.

    Returns:
        A new DataFrame with normalised column names.

    Raises:
        ValueError: If two columns would end up with the same name, e.g.
            ``"Sample size"`` and ``"sample_size"`` in the same table.
    """
    
    name_mapper = {}
    col_names = df.columns
    for old_name in col_names:
        new_name = normalise_name(old_name)
        name_mapper.update({old_name: new_name})

    #handle name duplication risk 
    #name_counts is a counter object, name_counts.values()
    name_counts = Counter(name_mapper.values())

    clashing_names = []
    for name, count in name_counts.items():
        if count > 1:
            clashing_names.append(name)

    if clashing_names:
        clashing_columns = []
        for old_name, new_name in name_mapper.items():
            if new_name in clashing_names:
                clashing_columns.append(old_name)

        raise ValueError(
            f"Columns {clashing_columns} would be renamed to the same name: "
            f"{clashing_names}"
        )
    

    df_with_cols_renamed = df.rename(columns=name_mapper)
    return df_with_cols_renamed


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
    names = []
    for df in df_dict.values():
        names.extend(df.columns)
    names_df = pd.Series(names)
    return names_df.value_counts()
        


def get_unique_column_names(df_dict: dict[str, pd.DataFrame]) -> list[str]:
    """List the unique column names across all tables, after normalising them.

    Each name is normalised with ``normalise_name`` before duplicates
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
