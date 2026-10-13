variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "env" {
  description = "Development environment (e.g. Dev, Stage, Prod)"
  type        = string
}

variable "region" {
  description = "Project GCP region"
  type        = string
}

variable "email_list" {
  description = "List of emails to receive email alerts"
  type        = map(string)
  sensitive   = true
}

variable "github_repo" {
  description = "Project GitHub repository (Format: owner/repository)"
  type        = string
}

variable "raw_dataset" {
  description = "Bigquery dataset pulled from 3 API store-channels"
}

variable "publish_dataset" {
  description = "Bigquery dataset containing BI ready datasets"
}
