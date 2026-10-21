import os
import sys

from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal

HOST = os.environ["DATABRICKS_HOST"].replace("https://", "").rstrip("/")
HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]
CATALOG = os.environ.get("CATALOG_NAME", "salesforce_dev")

# env prefix -> what that identity must see
EXPECTED = {
    "STEWARD_AU": dict(rows=516, countries={None, "Australia"}, pii=True),
    "STEWARD_US": dict(rows=3,   countries={"United States"},   pii=True),
    "STEWARD_EU": dict(rows=1,   countries={"France"},          pii=True),
    "ANALYST":    dict(rows=516, countries={None, "Australia"}, pii=False),
}


def fetch_rows(prefix, query):
    cfg = Config(
        host=f"https://{HOST}",
        client_id=os.environ[f"SP_{prefix}_ID"],
        client_secret=os.environ[f"SP_{prefix}_SECRET"],
    )
    with sql.connect(
        server_hostname=HOST,
        http_path=HTTP_PATH,
        credentials_provider=lambda: oauth_service_principal(cfg),
    ) as conn, conn.cursor() as cur:
        cur.execute(query)
        
        return cur.fetchall()


def check(name, ok):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    return ok

def quarantine_denied(prefix):
    try:
        query_silver_contact_quarantine = f"SELECT 1 FROM {CATALOG}.silver.contact_quarantine LIMIT 1"
        fetch_rows(prefix, query_silver_contact_quarantine)
        return False    # the query succeeded, so access was NOT denied
    except Exception as e:
        PERMISSION_ERROR_KEYWORDS = ("PERMISSION", "INSUFFICIENT_PERMISSIONS")
        # Convert error to string and check case-insensitively for permission keywords
        error_msg = str(e).upper()
        if any(keyword in error_msg for keyword in PERMISSION_ERROR_KEYWORDS):
            return True
        raise  # Re-raise unexpected errors (network drops, timeouts, auth token expiry)


failed = False
query_silver_contact = f"""SELECT mailing_country, first_name, email, birth_date
                            FROM {CATALOG}.silver.contact
                        """
for prefix, exp in EXPECTED.items():
    print(prefix)
    rows = fetch_rows(prefix, query_silver_contact)
    names = [r[1] for r in rows if r[1] is not None]
    emails = [r[2] for r in rows if r[2] is not None]
    dobs = [r[3] for r in rows if r[3] is not None]
    results = [
        check(f"row count == {exp['rows']} (got {len(rows)})", len(rows) == exp["rows"]),
        check("only allowed countries", {r[0] for r in rows} <= exp["countries"]),
    ]
    if exp["pii"]:
        results.append(check("real names", all(n != "***" for n in names)))
        results.append(check("real emails", all(not e.startswith("***") for e in emails)))
    else:
        results.append(check("names masked", all(n == "***" for n in names)))
        results.append(check("emails masked", all(e.startswith("***@") for e in emails)))
        results.append(check("birth dates hidden", len(dobs) == 0))
    results.append(check("quarantine table denied", quarantine_denied(prefix)))
    if prefix == "STEWARD_AU":
        results.append(check("sees some real birth dates", len(dobs) > 0))
    failed = failed or not all(results)

sys.exit(1 if failed else 0)