locals {
  name_suffix = "${var.project_name}-${var.environment}"
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.name_suffix}"
  location = var.location
}

data "azurerm_storage_account" "shared" {
  name                = var.shared_storage_account_name
  resource_group_name = var.shared_storage_account_resource_group_name
}

resource "azurerm_storage_container" "salesforce" {
  name                  = "salesforce"
  storage_account_id    = data.azurerm_storage_account.shared.id
  container_access_type = "private"
}

resource "azurerm_storage_data_lake_gen2_path" "managed" {
  path               = "managed"
  storage_account_id = data.azurerm_storage_account.shared.id
  filesystem_name    = azurerm_storage_container.salesforce.name
  resource           = "directory"
}
