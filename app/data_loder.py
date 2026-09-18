from pathlib import Path

import duckdb
import pandas as pd

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "support_tickets.csv"

TABLE_NAME = "support_tickets"

REQUIRED_COLUMNS = [
    "ticket_id",
    "created_at",
    "category",
    "priority",
    "status",
    "response_time_hrs",
    "resolution_time_hrs",
    "agent_id",
    "customer_rating",
    "issue_summary",
]

NUMERIC_COLUMNS = [
    "response_time_hrs",
    "resolution_time_hrs",
    "customer_rating",
]

TEXT_COLUMNS = [
    "ticket_id",
    "category",
    "priority",
    "status",
    "agent_id",
    "issue_summary",
]

# CSV Loading

def load_csv(csv_path: str | Path = DEFAULT_CSV_PATH) -> pd.DataFrame:
 
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Support ticket CSV file not found: {csv_path}"
        )

    if not csv_path.is_file():
        raise ValueError(
            f"CSV path is not a file: {csv_path}"
        )

    try:
        df = pd.read_csv(
            csv_path,
            encoding="utf-8",
        )
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"CSV file must be UTF-8 encoded: {csv_path}"
        ) from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            f"CSV file is empty: {csv_path}"
        ) from exc
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"Could not parse CSV file: {csv_path}"
        ) from exc

    if df.empty:
        raise ValueError(
            f"CSV file contains no data rows: {csv_path}"
        )

    return df

# Schema Validation

def validate_columns(df: pd.DataFrame) -> None:

    actual_columns = list(df.columns)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in actual_columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(missing_columns)
        )

# Data Cleaning

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
  
    cleaned_df = df.copy()

    # Normalize column names.
    cleaned_df.columns = [
        str(column).strip()
        for column in cleaned_df.columns
    ]

    # Strip unnecessary whitespace from text fields.
    for column in TEXT_COLUMNS:
        if column in cleaned_df.columns:
            cleaned_df[column] = cleaned_df[column].apply(
                lambda value: value.strip()
                if isinstance(value, str)
                else value
            )

    # Convert created_at into datetime.
    cleaned_df["created_at"] = pd.to_datetime(
        cleaned_df["created_at"],
        errors="coerce",
    )

    # Convert numeric columns.
    for column in NUMERIC_COLUMNS:
        cleaned_df[column] = pd.to_numeric(
            cleaned_df[column],
            errors="coerce",
        )

    return cleaned_df

# Data Quality Validation

def validate_data(df: pd.DataFrame) -> None:
 
    if df.empty:
        raise ValueError("No data rows are available after cleaning.")

    # ticket_id

    if df["ticket_id"].isna().any():
        raise ValueError(
            "Data validation failed: ticket_id contains NULL values."
        )

    if df["ticket_id"].duplicated().any():
        duplicate_ids = (
            df.loc[df["ticket_id"].duplicated(), "ticket_id"]
            .astype(str)
            .tolist()
        )

        preview = ", ".join(duplicate_ids[:10])

        raise ValueError(
            "Data validation failed: duplicate ticket_id values found. "
            f"Examples: {preview}"
        )

    # created_at

    invalid_dates = df["created_at"].isna()

    if invalid_dates.any():
        invalid_count = int(invalid_dates.sum())

        raise ValueError(
            "Data validation failed: "
            f"{invalid_count} invalid created_at value(s) found."
        )

    # Required categorical fields

    for column in ["category", "priority", "status", "agent_id"]:
        if df[column].isna().any():
            raise ValueError(
                f"Data validation failed: {column} contains NULL values."
            )

    # Numeric validation

    for column in NUMERIC_COLUMNS:
        non_null_values = df[column].dropna()

        if (non_null_values < 0).any():
            raise ValueError(
                f"Data validation failed: {column} contains "
                "negative values."
            )

    # Customer rating

    rating_values = df["customer_rating"].dropna()

    if not rating_values.empty:
        if (rating_values < 1).any() or (rating_values > 5).any():
            raise ValueError(
                "Data validation failed: customer_rating must "
                "be between 1 and 5."
            )

# Prepare Data

def prepare_data(
    csv_path: str | Path = DEFAULT_CSV_PATH,
) -> pd.DataFrame:

    df = load_csv(csv_path)

    validate_columns(df)

    df = clean_data(df)

    validate_data(df)

    return df

# DuckDB

def create_database(
    df: pd.DataFrame,
) -> duckdb.DuckDBPyConnection:

    connection = duckdb.connect(database=":memory:")

    connection.register(TABLE_NAME, df)

    return connection


def load_database(
    csv_path: str | Path = DEFAULT_CSV_PATH,
) -> duckdb.DuckDBPyConnection:

    df = prepare_data(csv_path)

    connection = create_database(df)

    return connection

# Convenience Function

def get_data_summary(
    connection: duckdb.DuckDBPyConnection,
) -> dict:

    row_count = connection.execute(
        f"SELECT COUNT(*) FROM {TABLE_NAME}"
    ).fetchone()[0]

    column_count = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_name = '{TABLE_NAME}'
        """
    ).fetchone()[0]

    return {
        "table": TABLE_NAME,
        "rows": row_count,
        "columns": column_count,
    }

# Local Test

if __name__ == "__main__":
    
    connection = load_database()

    summary = get_data_summary(connection)

    print("Data loading successful.")
    print(f"Table: {summary['table']}")
    print(f"Rows: {summary['rows']}")
    print(f"Columns: {summary['columns']}")

    connection.close()