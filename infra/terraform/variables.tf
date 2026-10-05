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
  sensitive   = true
}

variable "shared_storage_account_name" {
  description = "Shared storage account name"
  type        = string
  sensitive   = true
}

variable "allowed_ip_ranges" {
  description = "Public IP addresses allowed to reach storage and Key Vault data-plane"
  type        = list(string)
  sensitive   = true
}

variable "start_allowed_ip" {
  description = "Start public IP address allowed to reach sql server"
  type        = string
  sensitive   = true
}

variable "end_allowed_ip" {
  description = "End public IP address allowed to reach sql server"
  type        = string
  sensitive   = true
}
