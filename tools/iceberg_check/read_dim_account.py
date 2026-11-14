import os
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "uc",
    **{
        "type": "rest",
        "uri": f"https://{os.environ['DATABRICKS_HOST']}/api/2.1/unity-catalog/iceberg-rest",
        "warehouse": "salesforce_dev",
        "token": os.environ["DATABRICKS_TOKEN"],
        "header.X-Iceberg-Access-Delegation": "vended-credentials",
    },
)

print(catalog.list_namespaces())

table = catalog.load_table("gold.dim_account")
data = table.scan().to_arrow()
print(data.num_rows)
print(data.slice(0, 5).to_pandas())