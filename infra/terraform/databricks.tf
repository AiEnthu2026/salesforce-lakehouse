variable "shared_databricks_workspace_name" {
  description = "Shared databricks workspace name"
  type        = string
  sensitive   = true
}

variable "shared_databricks_workspace_resource_group_name" {
  description = "Shared databricks workspace resource group name"
  type        = string
  sensitive   = true
}

data "azurerm_databricks_workspace" "shared" {
  name                = var.shared_databricks_workspace_name
  resource_group_name = var.shared_databricks_workspace_resource_group_name
}

provider "databricks" {
  host = "https://${data.azurerm_databricks_workspace.shared.workspace_url}"
}

resource "azurerm_databricks_access_connector" "salesforce" {
  name                = "dbac-salesforce-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "salesforce_connector_delegator" {
  scope                = data.azurerm_storage_account.shared.id
  role_definition_name = "Storage Blob Delegator"
  principal_id         = azurerm_databricks_access_connector.salesforce.identity[0].principal_id
}

resource "azurerm_role_assignment" "salesforce_connector_storage" {
  scope                = azurerm_storage_container.salesforce.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.salesforce.identity[0].principal_id
}

resource "databricks_storage_credential" "salesforce" {
  name = "cred-salesforce-${var.environment}"

  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.salesforce.id
  }
}

resource "databricks_external_location" "salesforce_managed" {
  name            = "extloc-salesforce-${var.environment}"
  url             = "abfss://${azurerm_storage_container.salesforce.name}@${data.azurerm_storage_account.shared.name}.dfs.core.windows.net/managed"
  credential_name = databricks_storage_credential.salesforce.name
  comment         = "Managed storage root for the salesforce catalog"
}

resource "databricks_catalog" "salesforce" {
  name         = "${var.project_name}_${var.environment}"
  storage_root = databricks_external_location.salesforce_managed.url
  comment      = "Salesforce lakehouse: bronze/silver/gold"
}