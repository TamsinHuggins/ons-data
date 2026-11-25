# ONS Mental Health & Social Isolation Data Pipeline

A reproducible Python pipeline that turns an ONS spreadsheet into a clean, validated dataset that is ready for analysis. It is built to support one specific analytical question about depression and social isolation.

> **Status:** 🚧 In active development. See [Roadmap](#roadmap) for what is done and what is next.

---

## Contents

- [Purpose](#purpose)
- [Data source](#data-source)
- [Quick start](#quick-start)
- [Pipeline overview](#pipeline-overview)
- [Project structure](#project-structure)
- [Outputs](#outputs)
- [Data quality: issues found and decisions made](#data-quality-issues-found-and-decisions-made)
- [Testing](#testing)
- [Development workflow](#development-workflow)
- [Skills demonstrated](#skills-demonstrated)
- [AI-assisted development](#ai-assisted-development)
- [Roadmap](#roadmap)

---

## Purpose

**User:** a data scientist investigating mental health and social connection.

**Question they need to answer:**

> _How much more socially isolated are people with depressive symptoms?_

The ONS publishes the relevant estimates in a spreadsheet laid out for people to read, not for code to process. Each table sits under rows of notes, the header row is in a different place on different sheets, units vary between tables, and some cells contain suppression markers in place of numbers. This project prepares that data so the question can be answered quickly and reproducibly, and can be answered again when ONS publishes the next release.

The relevant tables are:

| Table    | Measure of social connection                                                   |
| -------- | ------------------------------------------------------------------------------ |
| Table_4  | Trust in most people (mean score, 0–10)                                        |
| Table_5  | Trust in most people (% with high trust)                                       |
| Table_6  | "I feel like I belong to this neighbourhood" (% agreeing)                      |
| Table_7  | "I can rely on the people in my life if I have a serious problem" (% agreeing) |
| Table_11 | How often people feel lonely (%)                                               |

Each table includes a breakdown by **depression indicator**: no or mild symptoms vs moderate to severe symptoms.

---

## Data source

|                 |                                                                                                            |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| **Publication** | Public opinions and social trends, Great Britain: mental health, 2 to 27 April 2025                        |
| **Publisher**   | Office for National Statistics (ONS)                                                                       |
| **Survey**      | Opinions and Lifestyle Survey (OPN)                                                                        |
| **Published**   | 16 May 2025                                                                                                |
| **Coverage**    | Adults aged 16 and over, Great Britain                                                                     |
| **Licence**     | [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) |

**Raw data is not committed to this repository.** To run the pipeline, download the `.xlsx` file from the ONS website and save it as:

```
data/raw/mentalhealth2to27april2025.xlsx
```

---

## Quick start

Requires Python 3.11+.

```bash
# 1. Clone and enter the project
git clone https://github.com/TamsinHuggins/ons-data.git
cd ons-data

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux

# 3. Install the package and development tools
python -m pip install -e ".[dev]"

# 4. Run the tests
python -m pytest

# 5. Run the pipeline
python -m ons_mental_health.pipeline
```

---

## Pipeline overview

```mermaid
flowchart LR
    A["Raw ONS workbook<br/>data/raw/"] -->|load.py| B["11 tables<br/>(dict of DataFrames)"]
    B -->|transform.py| C["One unioned table"]
    C -->|clean.py| D["Cleaned table<br/>data/interim/"]
    D -.->|validate.py| E["Analysis-ready dataset<br/>data/processed/"]
    E -.-> F["Analysis notebook"]
```

Solid arrows are implemented; dashed arrows are [planned](#roadmap).

| Stage       | Module                                               | What it does                                                                                                                                                   |
| ----------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Load        | [`load.py`](src/ons_mental_health/load.py)           | Reads each sheet's **named Excel table**, the exact cell range ONS defines for the data, so notes above and below each table are excluded automatically        |
| Transform   | [`transform.py`](src/ons_mental_health/transform.py) | Standardises column names, adds a `source_table` column so every row can be traced back to its table, and stacks all tables into one, matching columns by name |
| Clean       | [`clean.py`](src/ons_mental_health/clean.py)         | Replaces suppression markers with missing values, converts estimates to numbers and flags suppressed rows                                                      |
| Orchestrate | [`pipeline.py`](src/ons_mental_health/pipeline.py)   | Runs the stages in order and writes the output. It is the only module that reads or writes files                                                               |

<!-- Add a row for each new stage (clean, validate) as it is implemented. -->

---

## Project structure

```
ons-data/
├── data/
│   ├── raw/            # Original ONS download, never edited (git-ignored)
│   ├── interim/        # Intermediate outputs, e.g. the cleaned table (git-ignored)
│   └── processed/      # Final analysis-ready data (git-ignored)
├── docs/               # Methodology and supporting documentation
├── notebooks/          # Exploratory work; not the source of truth
├── src/
│   └── ons_mental_health/
│       ├── load.py       # Excel workbook → DataFrames
│       ├── transform.py  # Normalise, add provenance, union
│       ├── clean.py      # Suppression markers, numeric types
│       └── pipeline.py   # Entry point: runs all stages
├── tests/              # Unit tests (pytest)
├── pyproject.toml      # Package metadata and dependencies
└── README.md
```

---

## Outputs

| File                                                  | Stage   | Description                                                                                                                                                                                                 |
| ----------------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data/interim/mentalhealth2to27april2025_cleaned.csv` | Interim | All 11 data tables stacked into one table (572 rows). Column names standardised; suppression markers replaced and flagged (8 rows); estimates and confidence limits numeric. Further cleaning still planned |

<!-- Add processed outputs here as they are produced. -->

### Data dictionary: cleaned table

| Column                            | Description                                                                                                 |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `source_table`                    | ONS table the row came from, e.g. `Table_4`                                                                 |
| `breakdown_category`              | Grouping variable, e.g. `Age bands`, `Sex`, `Depression indicator`                                          |
| `breakdown`                       | Group within the category, e.g. `Moderate to severe symptoms`                                               |
| `response_options`                | Survey answer the estimate refers to, e.g. `Agree` (empty for mean-score tables)                            |
| `estimate_(%)`                    | Percentage of the group giving that response                                                                |
| `estimate_(mean_score_out_of_10)` | Mean score, for Tables 4 and 9 only                                                                         |
| `lcl`, `ucl`                      | Lower and upper 95% confidence limits. **Units match whichever estimate column is filled in**               |
| `sample_size`                     | Number of respondents, rounded to the nearest 10                                                            |
| `weighted_count`                  | Population the group represents, after survey weighting                                                     |
| `notes`                           | ONS note references, e.g. `[note 4]` marks a derived total category                                         |
| `is_suppressed`                   | `True` if ONS suppressed any of the estimate or confidence-limit values on this row; those values are empty |

A column that does not exist in a given source table is left empty (NaN) for that table's rows.

---

## Data quality: issues found and decisions made

A log of every data issue found, and how it was handled. Each decision is implemented in code and covered by tests wherever possible.

| #   | Issue                                                                                                              | Decision                                                                                                                                                                                                                                        | Status     |
| --- | ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| 1   | Each sheet has rows of notes above the table, and the header row varies between sheets (row 10 or 11)              | Read each sheet's **named Excel table** rather than guessing the header row. This is robust to layout changes in future releases                                                                                                                | ✅ Done    |
| 2   | Column names contain spaces and capitals, and could differ in style between tables                                 | Normalise to `lower_snake_case` **before** combining, so matching columns line up rather than producing duplicate half-empty columns                                                                                                            | ✅ Done    |
| 3   | Normalising could make two different columns in one table end up with the same name                                | Raise a `ValueError` naming the clashing columns rather than silently overwriting one of them                                                                                                                                                   | ✅ Done    |
| 4   | Combining tables loses track of where each row came from, and `lcl`/`ucl` mean different units in different tables | Add a `source_table` column to every row before combining                                                                                                                                                                                       | ✅ Done    |
| 5   | Tables have different sets of columns                                                                              | Union by column name; missing values become NaN. Every column is kept, so no information is lost                                                                                                                                                | ✅ Done    |
| 6   | Row labels (the index) repeat after stacking tables                                                                | Reset to a fresh index starting at 0                                                                                                                                                                                                            | ✅ Done    |
| 7   | An empty input would silently produce empty outputs                                                                | Fail loudly with a clear error message                                                                                                                                                                                                          | ✅ Done    |
| 8   | Suppression markers (`[c]`, `[w]`, `[low]`) in numeric columns make them text                                      | Convert to NaN, convert the columns to numbers, and flag affected rows with `is_suppressed`. Any unexpected text raises an error. Simplification: the marker type is not kept, so `[w]` (a true zero) can't be told apart from `[c]` (withheld) | ✅ Done    |
| 9   | Inconsistent labels, e.g. `Strongly Agree or Agree` vs `Strongly agree or Agree`                                   | Standardise text values                                                                                                                                                                                                                         | 🔲 Planned |
| 10  | Derived total rows (`[note 4]`) sit alongside the detailed categories, risking double counting                     | Flag them with an `is_derived` column rather than deleting them                                                                                                                                                                                 | 🔲 Planned |
| 11  | Two estimate columns with different units                                                                          | Combine into `estimate` plus a `unit` column                                                                                                                                                                                                    | 🔲 Planned |

<!-- Add new issues as they are discovered; update Status as they are resolved. -->

**ONS suppression markers** (from the workbook's Cover sheet):

| Marker   | Meaning                                                                         |
| -------- | ------------------------------------------------------------------------------- |
| `[c]`    | Suppressed: based on fewer than 3 respondents (quality and confidentiality)     |
| `[w]`    | No people estimated to be in this category                                      |
| `[low]`  | Estimate is less than 1 but not zero                                            |
| `[high]` | Estimate is more than 99                                                        |
| `[u]`    | Suppressed: the breakdown is based on 10 or fewer respondents (low reliability) |
| `[x]`    | Not available, e.g. the question was not asked                                  |

The markers to handle are set in `pipeline.py` and passed to the cleaning function, so they can be updated for future releases without changing the cleaning code.

---

## Testing

Tests are written with **pytest**, mostly using **test-driven development**: for each function, the tests and docstring are written first to define its behaviour, the tests are run to confirm they fail, and code is written to make them pass.

```bash
python -m pytest                 # run all tests
python -m pytest -v              # list each test and its result
python -m pytest -k union_tables # run only tests whose name matches
python -m pytest -rP             # also show printed output for passing tests
```

**Current status:** 28 tests passing.

<!-- Update the count when tests are added. -->

| Test file                                            | Covers                                                                                                       |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [`tests/test_transform.py`](tests/test_transform.py) | Name normalisation, clash detection, column counting, provenance column, table union                         |
| [`tests/test_clean.py`](tests/test_clean.py)         | Suppression markers: conversion to NaN, numeric types, row flag, unexpected values, configurable marker list |

<!-- Add a row for each new test file. -->

How the tests are written:

- **Small, self-contained test data.** Tests build tiny DataFrames in code rather than reading the real spreadsheet, so they run anywhere, including CI, and run quickly.
- **One behaviour per test,** named after the behaviour it checks, so a failure shows exactly what broke.
- **Fixtures** for shared test data, and **parametrised tests** for checking many input/output pairs.
- **Edge cases and failure modes** are tested as well as the normal case: empty inputs, name clashes, unexpected values, and checking that inputs are not modified.
- **DataFrame comparisons** use `pandas.testing.assert_frame_equal`, through a helper that prints the result and expected tables side by side when a test fails.

---

## Development workflow

- **GitHub Flow:** `main` always works. Each piece of work happens on its own branch and is merged through a pull request.
- **Issues → branches → pull requests:** work is tracked as GitHub Issues, and each pull request links to its issue.
- **Small, focused commits** with messages describing what changed and why.
- **Data never enters git:** raw data, intermediate files and outputs are git-ignored. Notebook outputs are cleared before committing.

---

## Skills demonstrated

| Skill                             | Evidence in this project                                                                                                                                                                                                                                |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Unit testing**                  | pytest suite with fixtures, parametrisation, error-case tests (`pytest.raises` with message matching) and DataFrame equality checks                                                                                                                     |
| **Test-driven development**       | Tests and docstrings written before each implementation; red → green → refactor                                                                                                                                                                         |
| **Modular design**                | One responsibility per module (load / transform / clean / pipeline); small single-purpose functions; file reading and writing kept in the pipeline module only; settings such as suppression markers passed in from the pipeline rather than hard-coded |
| **Defensive programming**         | Errors raised early with clear messages for invalid input (empty input, column name clashes, unexpected text in numeric columns) rather than silently producing wrong results                                                                           |
| **Data engineering**              | Reading named tables from Excel with openpyxl; harmonising column names across tables; unioning tables with different columns; recording where each row came from; separate raw / interim / processed data stages                                       |
| **Data manipulation with pandas** | Building DataFrames, renaming columns, `concat` with index reset, `value_counts`, vectorised boolean masks (`isin`, `&`, `~`, `any`), type conversion with `to_numeric`, handling missing values                                                        |
| **Python packaging**              | `src/` layout, `pyproject.toml`, editable install, separate runtime and development dependencies                                                                                                                                                        |
| **Reproducibility**               | Project-root-anchored `pathlib` paths; one command runs the pipeline end to end; raw data is never modified                                                                                                                                             |
| **Code documentation**            | Google-style docstrings with `Args` / `Returns` / `Raises`; type hints throughout                                                                                                                                                                       |
| **Version control**               | Git with GitHub Flow; issues linked to pull requests                                                                                                                                                                                                    |

<!-- Add rows as new skills are demonstrated, e.g. CI, data validation, linting. -->

### Capabilities evidenced

| Capability                                                                                                           | How this project evidences it                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| _Identify the appropriate engineering support to design and provide products for the organisation_                   | Starts from a defined user and question; delivers a documented data product with a data dictionary; uses a reproducible, tested and packaged pipeline                                                              |
| _Recognise the processes and tools for cleansing and preparing data, and put reusable processes and checks in place_ | Data quality issues logged with recorded decisions; reusable, tested transformation and cleaning functions; unexpected values rejected rather than silently dropped; the pipeline can be re-run on future releases |
| _Use data manipulation and transformation tools_                                                                     | pandas and openpyxl used to extract, standardise, combine and reshape published statistics                                                                                                                         |

---

## Roadmap

- [x] Project structure, packaging and version control
- [x] Load all data tables from the workbook using named Excel tables
- [x] Normalise column names, with clash detection
- [x] Add a provenance (`source_table`) column
- [x] Union all tables into one interim dataset
- [x] Pipeline entry point writing to `data/interim/`
- [x] Cleaning: suppression markers → NaN plus an `is_suppressed` flag column
- [x] Cleaning: convert estimates and confidence limits to numeric types
- [x] Run the cleaning step in the pipeline
- [ ] Cleaning: standardise response labels
- [ ] Cleaning: flag derived total rows
- [ ] Cleaning: combine estimate columns into `estimate` + `unit`
- [ ] Validation checks (value ranges, `lcl ≤ estimate ≤ ucl`, expected columns, unexpected markers)
- [ ] Analysis-ready dataset for Tables 4–7 and 11 in `data/processed/`
- [ ] Analysis notebook: depression and social isolation, with confidence intervals
- [ ] Continuous integration (GitHub Actions running the tests)
- [ ] Linting and formatting with ruff
- [ ] Unit tests for `load.py`
