# Lab 8: Orchestrating Pipelines to Write into BigQuery Managed Iceberg Tables

In this lab, you will learn how to orchestrate a production-grade Spark ETL workflow using **Apache Airflow** (managed via **Google Cloud Composer**) to append data directly into an existing **BigQuery Managed Iceberg Table** on Cloud Storage.

To optimize compute costs, you will run a DAG that automates the lifecycle of an **ephemeral Dataproc cluster**:
1. **Create Dataproc Cluster:** Provision a cluster only when needed, pre-configured with the Apache Iceberg runtime.
2. **Submit PySpark ETL Job:** Execute a Spark script that reads raw csv telemetry data from GCS , calculates average temperatures,appends the results directly to the GCS storage folder.
3. **Delete Dataproc Cluster:** Immediately tear down the cluster upon job completion (or failure) to prevent ongoing compute charges.

```
       [ Cloud Composer / Apache Airflow ]
                       │
                       ▼
         ┌───────────────────────────┐
         │  Create Dataproc Cluster  │  <── Provision cluster on-demand
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │  Submit PySpark ETL Job   │  <── Read raw csv ➔ Aggregate ➔ Append to GCS Folder in Iceberg format
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │  Delete Dataproc Cluster  │  <── Tear down VMs (Cost failsafe)
         └───────────────────────────┘
                       
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- Cloud Shell activated.
- An active Cloud Composer (Airflow) environment.
- An existing raw Iceberg table `sensor_db.filtered_readings` stored in `gs://YOUR_PROJECT_ID-iceberg-warehouse/warehouse/` (created in Lab 3 / Lab 5).
- An existing BigQuery Managed Iceberg table **`dataset3.iceberg_tbl1`** pointing to GCS path `gs://YOUR_PROJECT_ID-iceberg-warehouse/warehouse/` (created in Lab 7).
- A GCS bucket named `gs://YOUR_PROJECT_ID-code-bin/` to store scripts and JAR files.

---

## Step 1: Understand the PySpark ETL Script (`spark_iceberg_etl.py`)

Open [spark_iceberg_etl.py](file:///d:/trainings/GCP_Big_Data_Pipelines/Lab8/spark_iceberg_etl.py) to inspect the code.
- **SparkSession Configurations:** Configures the Hadoop Catalog `gcs_hadoop_catalog` for GCS Iceberg reads/writes.
- **Source Table Read:** Loads `gcs_hadoop_catalog.sensor_db.filtered_readings`.
- **Transformation:** Computes average temperature grouped by `device_id`.
- **Schema Projection:** Renames `device_id` to `sensor_id`, adds a generated unique `id` column, and selects columns to match the target schema (`id`, `sensor_id`, `temperature`).
- **Direct GCS Append:** Appends the results directly to the GCS path of your BigQuery managed table (`gs://YOUR_PROJECT_ID-iceberg-warehouse/warehouse`) using `append` mode:
  ```python
  df_final.write.format("iceberg").mode("append").save(args.warehouse_path)
  ```

---

## Step 2: Understand the Airflow DAG (`dataproc_workflow_dag.py`)

Open [dataproc_workflow_dag.py](file:///d:/trainings/GCP_Big_Data_Pipelines/Lab8/dataproc_workflow_dag.py) to review the orchestrator.
- **`DataprocCreateClusterOperator`:** Spins up a cluster in `us-central1` using the `2.2-debian12` image. It sets the `spark:spark.jars` property to dynamically load the Iceberg runtime JAR.
- **`DataprocSubmitJobOperator`:** Submits the PySpark job, passing the GCS warehouse path of your BigQuery Managed Table (`gs://[PROJECT_ID]-iceberg-warehouse/warehouse`) as an argument.
- **`DataprocDeleteClusterOperator`:** Deletes the cluster. Crucially, it uses **`trigger_rule="all_done"`** to ensure the cluster is destroyed even if the Spark ETL job fails, preventing runaway cloud costs.

---

## Step 3: Create GCS Buckets, Download Iceberg JAR, and Upload Files

To enable Dataproc to read the execution script, JAR libraries, and input CSV data, you must configure your Cloud Storage buckets and upload the required files.

1. Activate Cloud Shell.
2. Navigate to the Lab 8 directory:
   ```bash
   cd ~/big_data_pipelines_gcp/Lab8
   ```
3. Set your project ID:
   ```bash
   export PROJECT_ID=your_project_id
   ```
4. Create the GCS buckets for code storage and the Iceberg warehouse (if they do not already exist):
   ```bash
   # Create the code binary bucket
   gcloud storage buckets create gs://${PROJECT_ID}-code-bin --location=us-central1 --project=${PROJECT_ID}

   # Create the Iceberg warehouse bucket (if not created in Lab 7)
   gcloud storage buckets create gs://${PROJECT_ID}-iceberg-warehouse --location=us-central1 --project=${PROJECT_ID}
   ```
5. Download the Apache Iceberg Spark runtime JAR:
   ```bash
   curl -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.5.2/iceberg-spark-runtime-3.5_2.12-1.5.2.jar
   ```
6. Upload the Iceberg runtime JAR to your code bucket:
   ```bash
   gcloud storage cp iceberg-spark-runtime-3.5_2.12-1.5.2.jar gs://${PROJECT_ID}-code-bin/libs/
   ```
7. Upload the PySpark ETL script to your code bucket:
   ```bash
   gcloud storage cp spark_iceberg_etl.py gs://${PROJECT_ID}-code-bin/dataproc/spark_iceberg_etl_lab8.py
   ```
8. Upload/Copy the `sensor.csv` file (from which Spark will read) to your Iceberg warehouse bucket:
   We will copy the telemetry CSV file `sensor_data.csv` from Lab 2 to GCS as `sensor.csv`:
   ```bash
   gcloud storage cp sensor_data.csv gs://${PROJECT_ID}-iceberg-warehouse/sensor.csv
   ```

---

## Step 4: Create or Ensure Cloud Composer (Airflow) Environment is Running

Before you can deploy and run the Airflow DAG, you must ensure that a Cloud Composer environment is active in your GCP project. 

If you do not have an active environment, run the following in **Cloud Shell** to create a Cloud Composer 2 instance (Note: Composer 2 creation takes 15–20 minutes):
```bash
export PROJECT_ID=your_project_id
export ENVIRONMENT_NAME="walmart-retail-composer"
export REGION="us-central1"

export COMPOSER_SA="composer-environment-sa"
export COMPOSER_SA_EMAIL="${COMPOSER_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create ${COMPOSER_SA} \
  --display-name="Cloud Composer Environment Service Account" \
  --project=${PROJECT_ID}

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${COMPOSER_SA_EMAIL}" \
  --role="roles/composer.worker"

# Create the Cloud Composer 2 environment in your region (uses pre-configured default service account)
gcloud services enable \
    composer.googleapis.com \
    compute.googleapis.com \
    iam.googleapis.com \
    serviceusage.googleapis.com \
    storage.googleapis.com \
    cloudresourcemanager.googleapis.com \
    --project=${PROJECT_ID}

gcloud composer environments create ${ENVIRONMENT_NAME} \
    --location=${REGION} \
    --image-version="composer-2.17.3-airflow-2.10.5" \
    --project=${PROJECT_ID}
```

---

## Step 5: Deploy the DAG to Cloud Composer

Copy the Airflow orchestrator script to your Composer DAG folder.

1. Retrieve your Cloud Composer DAG bucket URI:
   ```bash
   gcloud composer environments describe walmart-retail-composer \
     --location us-central1 \
     --format="value(config.dagGcsPrefix)"
   ```
2. Upload the DAG file (replace `<COMPOSER_DAG_BUCKET>` with the GCS URI returned from the command above):
   ```bash
   gcloud storage cp dataproc_workflow_dag.py <COMPOSER_DAG_BUCKET>/
   ```

---

## Step 6: Trigger and Monitor the Workflow

1. Navigate to the **Composer** page in the GCP Console.
2. Click the **Airflow web interface** link to open the Airflow UI.
3. Locate the DAG named **`lab8_dataproc_lifecycle_orchestration`** and click the **Trigger DAG** button.
4. Click on the DAG run to open the **Graph View**. Monitor the tasks:
   - `create_dataproc_cluster` (will take 2-3 minutes to provision)
   - `run_spark_iceberg_etl` (will take 1-2 minutes to execute transformations)
   - `delete_dataproc_cluster` (will tear down VMs immediately after)

---

## Step 7: Verify and Query the Appended Data in BigQuery

Because BigQuery Managed Iceberg tables read metadata on-the-fly, the new records appended by Spark are immediately visible in BigQuery with **zero-copy sync**!

1. Open the **BigQuery** console.
2. Run the following query to view all records in the table (including the new rows appended by Spark with IDs starting at `1006`):
   ```sql
   SELECT * 
   FROM dataset3.iceberg_tbl1 
   ORDER BY id DESC;
   ```

3. Run a **Time Travel Query** to inspect the table state *before* Spark appended the data (replace with a timestamp that matches your run history, e.g. 10 minutes ago):
   ```sql
   SELECT * 
   FROM dataset3.iceberg_tbl1 FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 10 MINUTE);
   ```
   *Observe that the dataset travels back in time, displaying only the 5 original rows and excluding the Spark-appended rows, proving complete transactional version tracking!*

---

## Step 8: Cleanup

Delete the dataset and connection created in the previous lab if you are done:
```sql
DROP TABLE IF EXISTS dataset3.iceberg_tbl1;
DROP SCHEMA IF EXISTS dataset3 CASCADE;
```
