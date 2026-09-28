variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "australiaeast"
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "project_name" {
  description = "Short name used as a prefix for all resource names"
  type        = string
  default     = "salesforce"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging or prod."
  }
}

variable "shared_storage_account_resource_group_name" {
  description = "Resource group name for the storage account shared"
  type        = string
}

variable "shared_storage_account_name" {
  description = "Shared storage account name"
  type        = string
}

variable "allowed_ip_ranges" {
  description = "Public IP addresses allowed to reach storage and Key Vault data-plane"
  type        = list(string)
  sensitive   = true
}
