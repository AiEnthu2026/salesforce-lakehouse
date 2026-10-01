resource "random_string" "sql_suffix" {
  length  = 4
  upper   = false
  special = false
}

variable "admin_username" {
  description = "Admin User Name"
  type        = string
  sensitive   = true
}

resource "azurerm_mssql_server" "contracts" {
  name                = "sql-salesforce-dev-${random_string.sql_suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  version             = "12.0"
  minimum_tls_version = "1.2"

  azuread_administrator {
    login_username              = "${var.admin_username}"
    object_id                   = data.azurerm_client_config.current.object_id
    azuread_authentication_only = true
  }
}

resource "azurerm_mssql_database" "contracts" {
  name        = "sqldb-contracts"
  server_id   = azurerm_mssql_server.contracts.id
  sku_name    = "Basic"
  max_size_gb = 2
}