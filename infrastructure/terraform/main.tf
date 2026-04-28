provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

resource "azurerm_resource_group" "edge" {
  name     = "rg-${var.project_name}-fleet-${var.environment}"
  location = var.location
}

# --- Fleet Control Hub (AKS) ---

resource "azurerm_kubernetes_cluster" "fleet_k8s" {
  name                = "aks-fleet-control-${var.environment}"
  location            = azurerm_resource_group.edge.location
  resource_group_name = azurerm_resource_group.edge.name
  dns_prefix          = "fleet-k8s"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }
}

# --- Fleet Metadata Store (Postgres) ---

resource "azurerm_postgresql_flexible_server" "fleet" {
  name                   = "psql-fleet-metadata-${var.environment}"
  resource_group_name    = azurerm_resource_group.edge.name
  location               = azurerm_resource_group.edge.location
  version                = "13"
  administrator_login    = "fleetadmin"
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "GP_Standard_D2ds_v4"
}

# --- Multi-Cloud Telemetry Sink (AWS S3) ---

resource "aws_s3_bucket" "telemetry_sink" {
  bucket = "db-edge-telemetry-sink-${var.environment}"
}

# --- Secure Fleet Secrets (Azure Key Vault) ---

resource "azurerm_key_vault" "vault" {
  name                        = "kv-fleet-${var.environment}"
  location                    = azurerm_resource_group.edge.location
  resource_group_name         = azurerm_resource_group.edge.name
  enabled_for_disk_encryption = true
  tenant_id                   = var.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"
}
