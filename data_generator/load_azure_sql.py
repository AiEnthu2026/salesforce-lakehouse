import csv
import os
import struct
import sys

import pyodbc
from azure.identity import AzureCliCredential

TABLE = "dbo.account_contracts"
COLUMNS = ["contract_id", "customer_ref", "contract_tier",
           "committed_monthly_aud", "contract_start", "contract_end", "modified_at"]
SQL_COPT_SS_ACCESS_TOKEN = 1256  # driver-specific pre-connect attribute


def connect():
    server = os.environ["SQL_SERVER"]      # server name only, not the FQDN
    database = os.environ["SQL_DATABASE"]
    driver = os.environ.get("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

    token = AzureCliCredential().get_token("https://database.windows.net/.default").token
    raw = token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(raw)}s", len(raw), raw)

    conn_str = (f"DRIVER={{{driver}}};SERVER={server}.database.windows.net;"
                f"DATABASE={database};Encrypt=yes;")
    return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            sys.exit(f"Unexpected header: {reader.fieldnames}")
        return [tuple(row[c] or None for c in COLUMNS) for row in reader]


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ("replace", "append"):
        sys.exit("usage: python load_azure_sql.py <csv_path> <replace|append>")
    path, mode = sys.argv[1], sys.argv[2]

    rows = read_rows(path)
    placeholders = ", ".join("?" * len(COLUMNS))
    insert_sql = f"INSERT INTO {TABLE} ({', '.join(COLUMNS)}) VALUES ({placeholders})"

    conn = connect()
    try:
        cur = conn.cursor()
        if mode == "replace":
            cur.execute(f"TRUNCATE TABLE {TABLE}")
        cur.executemany(insert_sql, rows)
        conn.commit()
        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        print(f"{mode}: loaded {len(rows)} rows, table now has {cur.fetchone()[0]}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()