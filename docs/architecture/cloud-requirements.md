# Cloud Requirements

_Target requirements this project was designed against. Not all are met yet; see Known gaps in the README_

- Governed object storage for a lakehouse, reachable from Databricks without static keys
- Workload identity with least privilege, and separate access for dev and prod
- Central secret store that Databricks jobs can read, with rotation
- Restricted network path to storage and secrets, with anything public listed openly
- Managed ingestion from a SaaS source (Salesforce), from files and from a relational database
- Orchestration that triggers a Databricks job when ingestion finishes
- Managed streaming compatible with Structured Streaming
- Audit logs for data access and admin actions, with alerting
- Cost visibility: tagging, budgets and per-project totals, plus idle cost
- Full reproducibility from Terraform, with time to provision from scratch
- Pipeline authentication that uses federated identity and needs no stored secrets
- Recovery: soft delete, versioning and retention