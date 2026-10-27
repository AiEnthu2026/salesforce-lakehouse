# Genie agent

A Databricks Genie agent for account-health questions, built on the dbt marts and Gold tables of the Salesforce lakehouse.

The agent lives in the workspace and isn't part of the bundle, and this folder (genie_agent/) is a record only

**Tables:** `mart_account_360`, `mart_account_monthly_health`, `dim_account`, `fact_usage`. The marts carry column descriptions from dbt (`persist_docs`), which Genie reads.

**Instructions (summary):**
- Grain: `mart_account_360` is one row per account, and `mart_account_monthly_health` is one row per account per month.
- The UNKNOWN account is excluded from customer health answers unless asked.
- `commit_status` values are under, on_track, over, no_usage and no_commitment, and all currency is AUD.
- "This month", "current" or "latest" means the latest `month_start`, and otherwise all months are used.
- Rates show their numerator and denominator.

## Benchmarks

`benchmarks.ipynb` holds 10 questions with ground-truth SQL. Expected values are not stored, since results depend on the data and the run date.

- **Result:** 9 of 10 on 28 Oct 2026 in Agent mode (earlier runs scored 10 of 10; the instructions were tuned against this set).
- **Failure:** question 7 (top 5 industries by escalation rate). The agent used the account-level mart and returned a rounded percentage. The counts and ranking were identical to the reference.
- **Severity:** low. Failures are triaged by severity: wrong figures or broken rules are fixed, and naming or shape differences with correct figures are noted.

## What went wrong along the way

- "This month" leaked into an all-time answer, which led to the narrower rule above.
- One of my own reference queries was wrong: ascending order puts nulls first in Spark SQL, so a shortfall query returned null rows until I filtered them out.

## Limits

- Synthetic data, small groups (70 to 100 cases per industry), so rankings are for demonstration only.
- Benchmarks can't be exported from the Genie UI, so the notebook is the record.
- Genie's judge compares SQL, so differences in how a query is written can fail a test. On question 7 it flagged a different table and denominator although the counts matched.
- Results vary from run to run, so a single pass rate is a snapshot.