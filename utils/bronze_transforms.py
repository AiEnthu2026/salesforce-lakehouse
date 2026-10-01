import re


def sanitize_column_name(name: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z_]+", "_", name.strip()).rstrip("_").lower()
    return cleaned or "col"


def sanitize_columns(df):
    new_names = [sanitize_column_name(c) for c in df.columns]
    if len(set(new_names)) != len(new_names):
        raise ValueError(f"Column names collide after sanitizing: {new_names}")
    return df.toDF(*new_names)