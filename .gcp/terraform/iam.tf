locals {
  service_accounts = [
    "github-actions-deployer-sa",
    "dbt-pipeline-sa",
    "airbyte-vm-sa"
  ]
}

resource "google_service_account" "platform_accounts" {
  for_each     = toset(local.service_accounts)
  account_id   = each.key
  display_name = "Managed by Terraform: ${each.key}"
  project      = var.project_id

  depends_on = [google_project_service.enabled_api]
}
