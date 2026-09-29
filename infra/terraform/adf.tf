resource "random_string" "adf_suffix" {
  length  = 4
  upper   = false
  special = false
}

resource "azurerm_data_factory" "salesforce" {
  name                = "adf-salesforce-${var.environment}-${random_string.adf_suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "adf_landing_writer" {
  scope                = azurerm_storage_container.salesforce.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.salesforce.identity[0].principal_id
}