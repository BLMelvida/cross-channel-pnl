terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">8.6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}


locals {
  services = [
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "run.googleapis.com",
    "compute.googleapis.com",
    "workflows.googleapis.com",
    "eventarc.googleapis.com",
    "cloudscheduler.googleapis.com",
    "iamcredentials.googleapis.com",
    "bigquery.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ]
}

resource "google_project_service" "enabled_api" {
  for_each           = toset(local.services)
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
