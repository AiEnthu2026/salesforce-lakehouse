resource "random_string" "adf_suffix" {
  length  = 4
  upper   = false
  special = false
}

variable "git_account_name" {
  description = "Git Account Name"
  type        = string
  sensitive   = false
}

resource "azurerm_data_factory" "salesforce" {
  name                = "adf-salesforce-${var.environment}-${random_string.adf_suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  identity {
    type = "SystemAssigned"
  }

  github_configuration {
    account_name    = "${var.git_account_name}"
    repository_name = "salesforce-lakehouse"
    branch_name     = "develop"
    root_folder     = "/adf"
    publishing_enabled = true
    git_url         = "https://github.com"
  }
}

resource "azurerm_role_assignment" "adf_landing_writer" {
  scope                = azurerm_storage_container.salesforce.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.salesforce.identity[0].principal_id
}