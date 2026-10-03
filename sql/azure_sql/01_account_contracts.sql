IF OBJECT_ID('dbo.account_contracts', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.account_contracts (
        contract_id           NVARCHAR(10)  NOT NULL PRIMARY KEY,
        customer_ref          NVARCHAR(20)  NOT NULL,
        contract_tier         NVARCHAR(20)  NOT NULL,
        committed_monthly_aud DECIMAL(12,2) NOT NULL,
        contract_start        DATE          NOT NULL,
        contract_end          DATE          NULL,
        modified_at           DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
    );
END