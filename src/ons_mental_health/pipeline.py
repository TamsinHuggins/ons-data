"""Run the pipeline: load the ONS workbook, combine and clean its tables, and save the result.

Run from the project root with:
    python -m ons_mental_health.pipeline
"""

from pathlib import Path

from openpyxl import load_workbook

from ons_mental_health.clean import handle_suppression_markers
from ons_mental_health.load import get_dfs_from_sheets, get_table_titles
from ons_mental_health.transform import union_tables

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "mentalhealth2to27april2025.xlsx"
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
CLEANED_TABLES_FILE = INTERIM_DATA_DIR / "mentalhealth2to27april2025_cleaned.csv"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
TABLE_QUESTIONS_FILE = PROCESSED_DATA_DIR / "table_questions.csv"

# Shorthand ONS uses in place of a number. See the workbook's Cover sheet.
SUPPRESSION_MARKERS = ["[c]", "[w]", "[low]", "[high]", "[u]", "[x]"]

# Columns that should hold numbers but may contain suppression markers.
VALUE_COLUMNS = ["estimate_(%)", "estimate_(mean_score_out_of_10)", "lcl", "ucl"]


def main() -> None:
    """Load every table from the raw workbook, union and clean them, and save as CSV."""
    workbook = load_workbook(RAW_DATA_FILE, data_only=True)
    df_dict = get_dfs_from_sheets(workbook)
    unioned_df = union_tables(df_dict)
    cleaned_df = handle_suppression_markers(unioned_df, VALUE_COLUMNS, SUPPRESSION_MARKERS)
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(CLEANED_TABLES_FILE, index=False)
    print(f"Saved {len(cleaned_df)} rows to {CLEANED_TABLES_FILE}")

    table_questions = get_table_titles(workbook)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    table_questions.to_csv(TABLE_QUESTIONS_FILE, index=False)
    print(f"Saved {len(table_questions)} table questions to {TABLE_QUESTIONS_FILE}")


if __name__ == "__main__":
    main()
