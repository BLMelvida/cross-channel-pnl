resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id = var.raw_dataset
  location   = var.region

  delete_contents_on_destroy = false
}

resource "google_bigquery_dataset" "publish_dataset" {
  dataset_id = var.publish_dataset
  location   = var.region

  delete_contents_on_destroy = false
}
