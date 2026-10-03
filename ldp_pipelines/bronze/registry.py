BRONZE_SOURCES = [
    {
        "table": "blob_usage",
        "landing_subpath": "blob_usage",
        "format": "csv",
        "glob": "*.csv",
        "options": {"header": "true", "cloudFiles.inferColumnTypes": "false"},
        "check_rescued": True,
    },
    {
        "table": "sf_account",
        "landing_subpath": "salesforce/account",
        "format": "parquet",
        "glob": "*.parquet",
        "options": {},
        "check_rescued": False,
    },
    {
        "table": "sf_contact",
        "landing_subpath": "salesforce/contact",
        "format": "parquet",
        "glob": "*.parquet",
        "options": {},
        "check_rescued": False,
    },
    {
        "table": "sf_case",
        "landing_subpath": "salesforce/case",
        "format": "parquet",
        "glob": "*.parquet",
        "options": {},
        "check_rescued": False,
    },
    {
        "table": "sql_account_contracts",
        "landing_subpath": "azure_sql/account_contracts",
        "format": "parquet",
        "glob": "*.parquet",
        "options": {},
        "check_rescued": False,
    },
    
]