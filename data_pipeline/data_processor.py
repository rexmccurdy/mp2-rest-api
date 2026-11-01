import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    length = len(df)
    df = df.drop_duplicates()
    logger.debug(f"Removed {length - len(df)} duplicate rows")
    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    
    if axis == "rows":
        length = len(df)
        df = df.dropna()
        length_after = len(df)
    elif axis == "columns":
        length = len(df.columns)
        df = df.dropna(axis=1)
        length_after = len(df.columns)
    else:
        raise ValueError(f"Axis unsupported: {axis}")
    logger.debug(f"Dropped {length - length_after} {axis} with missing values")
    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ["iqr", "zscore"]:
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Method not accepted: {method}")

    start_rows = len(df)
    for col in columns:
        if col not in df:
            logger.warning(f"{col} does not exist in this dataframe")
            continue

        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning(f"{col} is not numeric, so outliers cannot be computed")
            continue

        if method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3-q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            df = df[(df[col] >= lower) & (df[col] <= upper)]

        if method == "zscore":
            mean = df[col].mean()
            std = df[col].std()
            z_score = (df[col] - mean) / std
            df = df[z_score.abs() <= threshold]

    logger.debug(f"{start_rows - len(df)} rows removed using {method} method with a threshold of {threshold}")

    return df
        

def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config.get("processing", {})


    if processing.get("remove_duplicates"):
        df = remove_duplicates(df)

    if processing.get("missing", {}).get("enabled"):
        ax = processing.get("missing", {}).get("axis")
        df = handle_missing(df, ax)


    if processing.get("outliers", {}).get("enabled"):
    
        cols = processing.get("outliers", {}).get("columns")
        method = processing.get("outliers", {}).get("method")
        threshold = processing.get("outliers", {}).get("threshold")

        df = remove_outliers(df, cols, method, threshold)

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""

    report = {}
    report["rows_before"] = len(df_before)
    report["rows_after"] = len(df_after)
    report["rows_removed"] = len(df_before) - len(df_after)

    report["columns_before"] = len(df_before.columns)
    report["columns_after"] = len(df_after.columns)
    report["columns_removed"] = len(df_before.columns) - len(df_after.columns)    

    return report