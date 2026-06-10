# Lab 7: Workflow Orchestration with Cloud Composer and Ephemeral Dataproc Clusters

In this lab, you will learn how to orchestrate a production-grade Spark ETL workflow using **Apache Airflow** (managed via **Google Cloud Composer**). 

Running Dataproc clusters continuously is expensive. To optimize costs, you will build a DAG (Directed Acyclic Graph) that automates the lifecycle of an **ephemeral Dataproc cluster**:
1. **Create Dataproc Cluster:** Provision a cluster only when needed, pre-configured with Apache Iceberg libraries.
2. **Submit PySpark ETL Job:** Execute a Spark script that reads data from an existing Iceberg table on GCS, aggregates the records, and writes the summary to a target Iceberg table on GCS.
3. **Delete Dataproc Cluster:** Immediately tear down the cluster upon job completion (or failure) to prevent ongoing compute charges.

```
       [ Cloud Composer / Apache Airflow ]
                       │
                       ▼
         ┌───────────────────────────┐
         │  Create Dataproc Cluster  │  <── Spin up VM compute nodes on-demand
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │  Submit PySpark ETL Job   │  <── Read raw Iceberg -> Aggregation -> Write curated Iceberg
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │  Delete Dataproc Cluster  │  <── Tear down compute nodes (Failsafe cleanup)
         └───────────────────────────┘
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- Cloud Shell activated.
- An active Cloud Composer (Airflow) environment.
- An existing raw Iceberg table `sensor_db.filtered_readings` stored in `gs://YOUR_PROJECT_ID-iceberg-warehouse/warehouse/` (created in Lab 3 / Lab 5).
- A bucket named `gs://YOUR_PROJECT_ID-code-bin/` to store scripts and JAR files.

---

## Required IAM Permissions

To manage and query BigQuery Managed Iceberg Tables, ensure that the following IAM roles are granted. You can apply them using the `gcloud` CLI commands below:

### 1. Project-Level Roles (For the User executing DDL/queries)
- **To Create Tables:**
  - `BigQuery Data Owner` (`roles/bigquery.dataOwner`)
  - `BigQuery Connection Admin` (`roles/bigquery.connectionAdmin`)
- **To Query Tables:**
  - `BigQuery Data Viewer` (`roles/bigquery.dataViewer`)
  - `BigQuery User` (`roles/bigquery.user`)

**CLI Commands to Grant Project Roles:**
Run the following in Cloud Shell (replace `USER_EMAIL` with your logged-in Google account email):
```bash
export PROJECT_ID=$(gcloud config get-value project)
export USER_EMAIL="your-email@example.com" # e.g. student-xxx@upgradlabs.com

# Grant Table Creation Roles
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="user:${USER_EMAIL}" \
  --role="roles/bigquery.dataOwner"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="user:${USER_EMAIL}" \
  --role="roles/bigquery.connectionAdmin"

# Grant Table Querying Roles
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="user:${USER_EMAIL}" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="user:${USER_EMAIL}" \
  --role="roles/bigquery.user"
```

### 2. GCS Bucket-Level Roles (For the Connection Service Account)
Grant the GCS External Connection's Service Account (e.g. the service account starting with `bqcx-...`) the following roles on your GCS warehouse bucket:
- `Storage Object User` (`roles/storage.objectUser`) — Allow BigQuery to write, read, and delete data/metadata files.
- `Storage Legacy Bucket Reader` (`roles/storage.legacyBucketReader`) — Allow BigQuery to read bucket metadata.

**CLI Commands to Grant Bucket Roles:**
Run the following in Cloud Shell (replace `CONNECTION_SA` with the connection's service account email, and `BUCKET_NAME` with your GCS warehouse bucket):
```bash
export BUCKET_NAME="upgradlabs-1750853349290-dataflow-temp"
export CONNECTION_SA="bqcx-123456789-abcd@gcp-sa-bigquery-condel.iam.gserviceaccount.com"

# Grant Storage permissions to the Connection Service Account
gcloud storage buckets add-iam-policy-binding gs://${BUCKET_NAME} \
  --member="serviceAccount:${CONNECTION_SA}" \
  --role="roles/storage.objectUser"

gcloud storage buckets add-iam-policy-binding gs://${BUCKET_NAME} \
  --member="serviceAccount:${CONNECTION_SA}" \
  --role="roles/storage.legacyBucketReader"
```

---

## Step 1: Understand the PySpark ETL Script (`spark_iceberg_etl.py`)

Open [spark_iceberg_etl.py](file:///d:/trainings/GCP_Big_Data_Pipelines/Lab7/spark_iceberg_etl.py) to inspect the code.
- **SparkSession Configurations:** Dynamically configures the Hadoop Catalog `gcs_hadoop_catalog` for GCS Iceberg reads/writes.
- **Source Table Read:** Loads `gcs_hadoop_catalog.sensor_db.filtered_readings`.
- **Transformation:** Computes average temperature, average humidity, and total reading counts grouped by `device_id` and `date`.
- **Target Table Write:** Writes the aggregated summary to the target Iceberg table `gcs_hadoop_catalog.sensor_db.aggregated_readings` on GCS using `overwrite` mode.

---

## Step 2: Understand the Airflow DAG (`dataproc_workflow_dag.py`)

Open [dataproc_workflow_dag.py](file:///d:/trainings/GCP_Big_Data_Pipelines/Lab7/dataproc_workflow_dag.py) to review the orchestrator.
- **Dynamic Project Identifier:** Automatically resolves the active GCP Project ID using metadata credentials or environment fallbacks.
- **`DataprocCreateClusterOperator`:** Spins up a cluster in `us-central1` using the `2.2-debian12` image. It sets the `spark:spark.jars` property to dynamically load the Iceberg runtime JAR.
- **`DataprocSubmitJobOperator`:** Submits the PySpark job, passing the GCS warehouse path as an argument.
- **`DataprocDeleteClusterOperator`:** Deletes the cluster. Crucially, it uses **`trigger_rule="all_done"`** to ensure the cluster is destroyed even if the Spark ETL job fails, preventing runaway cloud costs.

---

## Step 3: Upload ETL Scripts and JAR files to GCS

To enable Dataproc to read the execution script and jar libraries, upload them to your GCS code bucket.

1. Activate Cloud Shell.
2. Navigate to the Lab 7 directory:
   ```bash
   cd ~/big_data_pipelines_gcp/Lab7
   ```
3. Set your project ID:
   ```bash
   export PROJECT_ID=$(gcloud config get-value project)
   ```
4. Upload the PySpark script:
   ```bash
   gcloud storage cp spark_iceberg_etl.py gs://${PROJECT_ID}-code-bin/dataproc/
   ```
5. Ensure the Iceberg runtime JAR is uploaded:
   ```bash
   gcloud storage cp ../iceberg-spark-runtime-3.5_2.12-1.5.2.jar gs://${PROJECT_ID}-code-bin/libs/
   ```

---

## Step 4: Deploy the DAG to Cloud Composer

Copy the Airflow orchestrator script to your Composer DAG folder.

1. Retrieve your Cloud Composer DAG bucket URI:
   ```bash
   gcloud composer environments describe YOUR_COMPOSER_ENVIRONMENT_NAME \
     --location us-central1 \
     --format="value(config.dagGcsPrefix)"
   ```
2. Upload the DAG file (replace `<COMPOSER_DAG_BUCKET>` with the GCS URI returned from the command above):
   ```bash
   gcloud storage cp dataproc_workflow_dag.py <COMPOSER_DAG_BUCKET>/
   ```

---

## Step 5: Trigger and Monitor the Workflow

1. Navigate to the **Composer** page in the GCP Console.
2. Click the **Airflow web interface** link to open the Airflow UI.
3. Locate the DAG named **`lab7_dataproc_lifecycle_orchestration`** and click the **Trigger DAG** button.
4. Click on the DAG run to open the **Graph View**. Monitor the tasks:
   - `create_dataproc_cluster` (will take 2-3 minutes to provision)
   - `run_spark_iceberg_etl` (will take 1-2 minutes to execute transformations)
   - `delete_dataproc_cluster` (will tear down VMs immediately after)

---

## Step 6: Verify the Output in BigQuery

Verify that the target table `aggregated_readings` has been successfully created and populated on GCS by creating a BigQuery external table.

1. Navigate to **BigQuery** in the GCP Console.
2. Run the following DDL statement in the SQL Editor to map the aggregated Iceberg table:
   ```sql
   CREATE OR REPLACE EXTERNAL TABLE `sensor_analytics.aggregated_readings_iceberg`
   OPTIONS (
     format = 'ICEBERG',
     uris = ['gs://YOUR_PROJECT_ID-iceberg-warehouse/warehouse/sensor_db/aggregated_readings/metadata/*.metadata.json']
   );
   ```
3. Query the aggregated statistics:
   ```sql
   SELECT * 
   FROM `sensor_analytics.aggregated_readings_iceberg` 
   ORDER BY date DESC, avg_temperature DESC;
   ```
