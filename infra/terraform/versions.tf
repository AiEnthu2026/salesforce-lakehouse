terraform {
  required_version = ">= 1.9.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"   # check registry for current version before typing
    }
  }

  backend "azurerm" {
    key                   = "salesforce-dev.tfstate"
    use_azuread_auth      = true
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}