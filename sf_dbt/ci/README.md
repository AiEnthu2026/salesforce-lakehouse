# Description

- `profiles.yml` is used by the CI gate.
- `dbt-grants.ipynb` is a manual one-time setup per environment, to be replaced by Terraform later.

### About the dbt-grants notebook

- When to run it: set the `env` widget to the target environment, and run it before the first dbt run in a new environment.
- What it grants: read-only on `gold`; write only on the environment's dbt schema.
