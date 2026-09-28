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