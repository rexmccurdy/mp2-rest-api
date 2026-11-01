# src/data_validator.py
import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    original_rows = len(df)
    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Required column '{col}' is missing from the DataFrame")
            raise ValueError(f"Required column '{col}' is missing from the DataFrame")

    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    # TODO: Log a warning and record this row's index.
                    logger.debug(f"Invalid value found in column '{col}' at row {i+1}: {value}")
                    invalid_rows.append(i)

        df = df.drop(invalid_rows)
 
    df[col] = pd.to_numeric(df[col])
    logger.debug(f"Valid rows remaining: {len(df)}. Removed {original_rows - len(df)} rows with invalid numeric values")
    return df
