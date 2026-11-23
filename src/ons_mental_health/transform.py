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
    #name_counts is a counter object, dictionary-like with name as index and count as value
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



def add_source_column(
    df: pd.DataFrame, table_name: str
) -> pd.DataFrame:
    """Return a copy of a DataFrame with a column titled source_table, recording which table it came from.

    The new column is added as the first column, with ``table_name`` on every
    row. This keeps rows traceable after tables are combined, which matters
    because tables can use the same columns for different units (e.g.
    ``lcl`` is a percentage in some tables and a score out of 10 in others).
    The input DataFrame is not modified.

    Args:
        df: A single table.
        table_name: The name to record, e.g. ``"Table_4"``.

    Returns:
        A new DataFrame with the source column first.

    Raises:
        ValueError: If ``df`` already has a column called ``source_table``.
    """

    df_with_source_col = df.copy()

    if "source_table" in df_with_source_col.columns:
        raise ValueError("source_table column already exists")
    
    df_with_source_col.insert(loc = 0, column = "source_table", value=table_name)
    return df_with_source_col


def union_tables(
    df_dict: dict[str, pd.DataFrame], min_tables: int = 2
) -> pd.DataFrame:
    """Combine all tables into one DataFrame, matching columns by name.

    Steps:
        1. Normalise each table's column names with ``normalise_column_names``.
        2. Add a source column to each table with ``add_source_column``.
        3. Stack the tables on top of each other. Where a table lacks a
           column that others have, its rows get missing values (NaN).

    The input tables are not modified.

    Args:
        df_dict: DataFrames keyed by table name, as returned by
            ``load.get_dfs_from_sheets``.
        min_tables: Passed to ``find_rare_columns``; columns found in fewer
            tables than this are dropped.

    Returns:
        One DataFrame containing every row from every table, with a
        ``source_table`` column first and a fresh index starting at 0.

    Raises:
        ValueError: If any table has column names that clash once
            normalised (raised by ``normalise_column_names``). Or, if df_dict is empty.


    """
    
    if len(df_dict) == 0:
        raise ValueError("No tables to process, dictionary is empty" )
        

    for_concat_df_dict : dict = dict()
    
    for table_name, df in df_dict.items():
        name_normalised_df = normalise_column_names(df)
        with_source_col_df = add_source_column(name_normalised_df, table_name)
        for_concat_df_dict[table_name] = with_source_col_df
    
    unioned_df = pd.concat(objs=for_concat_df_dict.values(), sort=False, ignore_index =True)
    return unioned_df
    
    