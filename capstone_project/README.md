# Walmart Retail Big Data Pipeline on GCP

This Capstone Project implements a production-grade, end-to-end streaming ingestion and batch processing retail data pipeline on Google Cloud Platform (GCP). The pipeline uses Pub/Sub, Dataflow (Apache Beam), Apache Iceberg on Google Cloud Storage (GCS), Dataproc (PySpark), Apache Airflow (Cloud Composer), and BigQuery.

---

## 1. Project Directory Structure

```
capstone_project/
├── requirements.txt            # Python environment dependencies
├── Explanation.md              # Architectural decisions and production blocker deep-dives
├── README.md                   # Setup and execution guide (This file)
├── schemas/                    # JSON schemas for data ingestion validation
│   ├── order_event.json
│   ├── inventory_event.json
│   └── customer_event.json
├── publisher/                  # Mock event simulator publishing to Pub/Sub
│   └── mock_events_publisher.py
├── dataflow/                   # Apache Beam pipeline running on Dataflow
│   └── streaming_pipeline.py
├── dataproc/                   # PySpark ETL batch job running on Dataproc
│   └── spark_etl_job.py
├── airflow/                    # Airflow Orchestration DAG
│   └── orchestration_dag.py
└── terraform/                  # Terraform configuration files
    └── main.tf
```

---

## 2. Prerequisites

Ensure you have the following installed on your machine:
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) authenticated to your GCP account.
- [Terraform](https://developer.hashicorp.com/terraform/downloads) (v1.3.0 or higher).
- [Python 3.9+](https://www.python.org/downloads/) installed.
- An active GCP Project with billing enabled.

---

## 3. Step-by-Step Setup and Execution

### Step 1: Initialize Local Python Environment
First, install the required packages:
```bash
pip install -r requirements.txt
```

---

### Step 2: Deploy GCP Infrastructure using Terraform
Deploy Pub/Sub topics, GCS buckets, BigQuery datasets, and external table schemas.

1. Navigate to the Terraform directory:
   ```bash
   cd terraform
   ```
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Plan and apply the deployment:
   ```bash
   # Replace with your actual GCP Project ID
   export PROJECT_ID=$(gcloud config get-value project)
   
   terraform plan -var="project_id=${PROJECT_ID}"
   terraform apply -var="project_id=${PROJECT_ID}" -auto-approve
   ```
4. Return to the project root:
   ```bash
   cd ..
   ```

---

### Step 3: Upload Spark Script and Libraries to GCS

To execute the Dataproc PySpark jobs, we must upload the code script and the required Apache Iceberg Spark Runtime JAR to our Code Bin GCS bucket.

1. Download the Apache Iceberg Spark Runtime JAR:
   ```bash
   # Download the runtime jar locally (Iceberg 1.5.2 with Spark 3.5 support)
   curl -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.5.2/iceberg-spark-runtime-3.5_2.12-1.5.2.jar
   ```
2. Upload the JAR to GCS:
   ```bash
   gcloud storage cp iceberg-spark-runtime-3.5_2.12-1.5.2.jar gs://${PROJECT_ID}-code-bin/libs/
   ```
3. Upload the Spark ETL script to GCS:
   ```bash
   gcloud storage cp dataproc/spark_etl_job.py gs://${PROJECT_ID}-code-bin/dataproc/
   ```

---

### Step 4: Run the Mock Events Publisher
The publisher generates randomized retail transaction, inventory, and customer loyalty records and publishes them to Pub/Sub.

1. Run the publisher:
   ```bash
   python publisher/mock_events_publisher.py --project ${PROJECT_ID} --interval 1.0
   ```
   *Leave this running in a separate terminal window to continuously feed data to your ingestion stream.*

---

### Step 5: Launch the Dataflow Streaming Pipeline
This job ingests raw streams from Pub/Sub, validates them against JSON schemas, and writes them to GCS in Apache Iceberg format.

1. Submit the Beam pipeline to Cloud Dataflow:
   ```bash
   python dataflow/streaming_pipeline.py \
     --project ${PROJECT_ID} \
     --warehouse_path gs://${PROJECT_ID}-iceberg-raw/warehouse \
     --runner DataflowRunner \
     --region us-central1 \
     --temp_location gs://${PROJECT_ID}-iceberg-raw/temp
   ```

2. Monitor the Dataflow Console to verify that the pipelines for `orders-events`, `inventory-events`, and `customer-events` are streaming successfully.

---

### Step 6: Deploy Airflow Orchestration DAG
Orchestrate the nightly batch processing, data quality validations, and Iceberg table maintenance.

1. Retrieve your Cloud Composer DAG bucket name:
   ```bash
   # List your composer environment to get the GCS DAGs bucket
   gcloud composer environments describe walmart-retail-composer --location us-central1 --format="value(config.dagGcsPrefix)"
   ```
2. Copy the DAG file to the Composer DAGs directory:
   ```bash
   gcloud storage cp airflow/orchestration_dag.py <COMPOSER_DAG_BUCKET>/
   ```
3. Trigger the DAG in the Airflow Web UI to verify execution:
   - **`create_dataproc_cluster`**: Provisions an ephemeral Dataproc cluster preconfigured with Spark/Iceberg runtimes.
   - **`run_spark_etl`**: Executes the Spark batch processing (aggregations, joins, and ACID `MERGE INTO` updates).
   - **`run_iceberg_maintenance`**: Executes metadata cleanups, expiring snapshots older than 7 days, and compacting manifest files.
   - **`delete_dataproc_cluster`**: Tears down the Dataproc cluster to save costs.
   - **`refresh_bigquery_reports`**: Materializes aggregation queries into BigQuery.
   - **`run_data_quality_checks`**: Ensures assertions (e.g., non-negative revenue) are satisfied.

---

## 4. Querying and Verifying the Output

Once the Spark job completes, query the curated tables directly from BigQuery without copying data.

### Query 1: Yesterday's Top Performing Stores (from `retail_analytics.daily_store_revenue`)
```sql
SELECT 
  store_id, 
  daily_revenue, 
  units_sold
FROM 
  `retail_analytics.daily_store_revenue`
ORDER BY 
  daily_revenue DESC 
LIMIT 5;
```

### Query 2: Low-Stock Inventory Alerts (from `retail_analytics.inventory_by_store_external`)
```sql
SELECT 
  store_id, 
  product_id, 
  quantity_on_hand, 
  last_updated
FROM 
  `retail_analytics.inventory_by_store_external`
WHERE 
  quantity_on_hand < 10
ORDER BY 
  quantity_on_hand ASC;
```

### Query 3: Customer Profiles with Loyalty Tier (from `retail_analytics.customer_360_external`)
```sql
SELECT 
  customer_id, 
  first_name, 
  last_name, 
  loyalty_tier
FROM 
  `retail_analytics.customer_360_external`
WHERE 
  loyalty_tier = 'PLATINUM';
```
*(Note: External tables in BigQuery are mapped to GCS paths using the `_external` suffix for separation of concern from raw views).*
