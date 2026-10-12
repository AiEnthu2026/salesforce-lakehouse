# sf_dbt

A dbt Core project over the Gold layer of this repository. It reads the seven Gold tables, builds one staging view per table, and tests keys, relationships and allowed values. It never writes to Gold.

![Lineage: 7 Gold sources to 7 staging views](../docs/dbt/lineage-graph.png)

## Status
The staging layer is complete. Models with business logic (marts) are not built yet.

## What is in it
- 7 sources: the Gold tables (3 dimensions, 2 facts, 2 aggregates)
- 7 staging views, written to the `dbt_dev` schema in the dev catalog
- 29 data tests: 7 unique, 15 not_null, 3 relationships, 4 accepted_values
- Last full run: 35 passed, 1 warning, 0 errors (7 views and 29 tests)

## Identity and access
dbt runs as its own Databricks service principal, not as a person and not with the shared token. It can read the Gold schema and create and write tables in `dbt_dev`. It has no access to Bronze, Silver, staging or prod. No credentials are stored in this repository.

## Run it
You need Python, a virtual environment with `requirements-dbt.txt` installed, a `profiles.yml` outside the repository, and these environment variables set in the same shell (names only):

- DBT_DATABRICKS_HOST
- DBT_HTTP_PATH
- DBT_CATALOG
- DBT_DATABRICKS_CLIENT_ID
- DBT_DATABRICKS_CLIENT_SECRET

The profile reads every value through `env_var`, so it holds no secrets:

```
sf_dbt:
  target: dev
  outputs:
    dev:
      type: databricks
      host: "{{ env_var('DBT_DATABRICKS_HOST') }}"
      http_path: "{{ env_var('DBT_HTTP_PATH') }}"
      catalog: "{{ env_var('DBT_CATALOG') }}"
      schema: dbt_dev
      auth_type: oauth
      client_id: "{{ env_var('DBT_DATABRICKS_CLIENT_ID') }}"
      client_secret: "{{ env_var('DBT_DATABRICKS_CLIENT_SECRET') }}"
      threads: 4
```

Then, from the `sf_dbt` folder:

```
dbt debug
dbt build --select staging -t dev
dbt docs generate
```

## Design choices
- **dbt consumes Gold and does not rebuild it.** The pipeline owns ingestion through Gold. dbt adds tests, documentation and (later) business logic on top.
- **Staging models are views with explicit column lists.** A new Gold column does not flow through silently, and each model documents what dbt depends on.
- **The aggregate tables get a built key.** `account_month_key` joins account and month so one unique test covers both columns, with not_null tests on the two source columns.
- **Separate write schema.** dbt writes only to `dbt_dev`, so a bad run cannot overwrite pipeline output.
- **Tests guard keys, relationships and allowed values.** They do not check that calculations are correct.

## Known issues
- 20 contacts reference 12 account IDs that are not in `dim_account`. The relationships test on `dim_contact` warns on this and fails if the count rises above 20. The pipeline fix (map orphan contacts to UNKNOWN, as the fact tables do) is on the backlog.
- "Staging" here means the model layer, not the staging environment.
- The service principal, the `dbt_dev` schema and the warehouse permission were created by hand, not in Terraform.
- CI does not run dbt yet.