resource "random_string" "source_suffix" {
  length  = 4
  special = false
  upper   = false
}

resource "azurerm_storage_account" "source_blob" {
  name                = "st${var.project_name}${var.environment}${random_string.source_suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = false

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false

  shared_access_key_enabled       = false
  default_to_oauth_authentication = true

  network_rules {
    default_action = "Deny"
    ip_rules       = var.allowed_ip_ranges
    bypass         = ["None"]

    private_link_access {
      endpoint_resource_id = azurerm_data_factory.salesforce.id
      endpoint_tenant_id   = data.azurerm_client_config.current.tenant_id
    }
  }

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_container" "src_blob_usage" {
  name                  = "src-blob-usage"
  storage_account_id    = azurerm_storage_account.source_blob.id
  container_access_type = "private"
}

resource "azurerm_role_assignment" "me_source_writer" {
  scope                = azurerm_storage_container.src_blob_usage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "adf_source_reader" {
  scope                = azurerm_storage_container.src_blob_usage.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_data_factory.salesforce.identity[0].principal_id
}

resource "azurerm_network_security_perimeter" "source_blob" {
  name                = "nsp-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "azurerm_network_security_perimeter_profile" "source" {
  name                          = "source-profile"
  network_security_perimeter_id = azurerm_network_security_perimeter.source_blob.id
}

resource "azurerm_network_security_perimeter_association" "storage" {
  name                                  = "storage-assoc"
  resource_id                           = azurerm_storage_account.source_blob.id
  access_mode                           = "Learning"
  network_security_perimeter_profile_id = azurerm_network_security_perimeter_profile.source.id
}

resource "azurerm_network_security_perimeter_access_rule" "allow_own_ip" {
  name                                  = "allow-own-ip"
  direction                             = "Inbound"
  network_security_perimeter_profile_id = azurerm_network_security_perimeter_profile.source.id

  address_prefixes = [for ip in var.allowed_ip_ranges : "${ip}/32"]
}