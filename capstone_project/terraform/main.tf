# Terraform Configuration for Walmart Retail Big Data Pipeline on GCP
# This file provisions Pub/Sub topics, GCS Buckets, and BigQuery Dataset/External Tables.

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.50.0"
    }
  }
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "project_id" {
  type        = string
  description = "The GCP Project ID where resources will be created"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "The GCP region for regional resources"
}

variable "zone" {
  type        = string
  default     = "us-central1-a"
  description = "The GCP zone for regional resources"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ---------------------------------------------------------------------------
# Pub/Sub Topics
# ---------------------------------------------------------------------------

resource "google_pubsub_topic" "orders_events" {
  name = "orders-events"
  
  labels = {
    pipeline = "walmart-retail"
    stream   = "orders"
  }
}

resource "google_pubsub_topic" "inventory_events" {
  name = "inventory-events"

  labels = {
    pipeline = "walmart-retail"
    stream   = "inventory"
  }
}

resource "google_pubsub_topic" "customer_events" {
  name = "customer-events"

  labels = {
    pipeline = "walmart-retail"
    stream   = "customer"
  }
}

# ---------------------------------------------------------------------------
# GCS Warehouse Buckets
# ---------------------------------------------------------------------------

resource "google_storage_bucket" "iceberg_raw" {
  name          = "${var.project_id}-iceberg-raw"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    layer = "raw"
    type  = "iceberg"
  }
}

resource "google_storage_bucket" "iceberg_curated" {
  name          = "${var.project_id}-iceberg-curated"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    layer = "curated"
    type  = "iceberg"
  }
}

resource "google_storage_bucket" "code_bin" {
  name          = "${var.project_id}-code-bin"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  labels = {
    purpose = "code-artifacts"
  }
}

# ---------------------------------------------------------------------------
# BigQuery Dataset
# ---------------------------------------------------------------------------

resource "google_bigquery_dataset" "retail_analytics" {
  dataset_id                  = "retail_analytics"
  friendly_name               = "Walmart Retail Analytics"
  description                 = "Dataset for curated data structures and reporting models"
  location                    = var.region
  default_table_expiration_ms = 3600000 * 24 * 7 # 7 days default retention

  labels = {
    env = "production"
  }
}

# ---------------------------------------------------------------------------
# BigQuery External Tables (Direct Iceberg queries on GCS)
# ---------------------------------------------------------------------------

resource "google_bigquery_table" "sales_daily_external" {
  dataset_id = google_bigquery_dataset.retail_analytics.dataset_id
  table_id   = "sales_daily_external"
  
  description = "External Iceberg table pointing to daily sales aggregator in GCS"

  external_data_configuration {
    autodetect    = true
    source_format = "ICEBERG"
    source_uris   = ["gs://${google_storage_bucket.iceberg_curated.name}/warehouse/curated_data/sales_daily/metadata/*.metadata.json"]
  }
}

resource "google_bigquery_table" "inventory_by_store_external" {
  dataset_id = google_bigquery_dataset.retail_analytics.dataset_id
  table_id   = "inventory_by_store_external"

  description = "External Iceberg table pointing to inventory-by-store in GCS"

  external_data_configuration {
    autodetect    = true
    source_format = "ICEBERG"
    source_uris   = ["gs://${google_storage_bucket.iceberg_curated.name}/warehouse/curated_data/inventory_by_store/metadata/*.metadata.json"]
  }
}

# ---------------------------------------------------------------------------
# IAM and Service Accounts
# ---------------------------------------------------------------------------

resource "google_service_account" "pipeline_runner" {
  account_id   = "walmart-pipeline-runner"
  display_name = "Walmart Retail Pipeline Service Account"
}

# Grant Storage Admin permissions on buckets
resource "google_storage_bucket_iam_member" "raw_admin" {
  bucket = google_storage_bucket.iceberg_raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

resource "google_storage_bucket_iam_member" "curated_admin" {
  bucket = google_storage_bucket.iceberg_curated.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

resource "google_storage_bucket_iam_member" "code_reader" {
  bucket = google_storage_bucket.code_bin.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

# Grant Pub/Sub permissions
resource "google_project_iam_member" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

# Grant BigQuery Connection User permission for external connections
resource "google_project_iam_member" "bq_connection_user" {
  project = var.project_id
  role    = "roles/bigquery.connectionUser"
  member  = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

# ---------------------------------------------------------------------------
# Cloud Composer Environment (Optional Orchestrator Provisioning)
# ---------------------------------------------------------------------------
# Note: Cloud Composer environments take 20-30 minutes to provision. 
# It is commented out here by default to prevent deployment delays and excess costs.
# Un-comment the block below if you wish to manage Composer via Terraform.

# resource "google_composer_environment" "retail_composer" {
#   name   = "walmart-retail-composer"
#   region = var.region
#
#   config {
#     software_config {
#       image_version = "composer-2.17.3-airflow-2.10.5"
#       env_variables = {
#         GCP_PROJECT = var.project_id
#       }
#     }
#
#     node_config {
#       service_account = google_service_account.pipeline_runner.email
#       zone            = var.zone
#     }
#   }
# }
