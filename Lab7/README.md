# Lab 7: BigQuery Managed Iceberg Tables — Transactional SQL and Time Travel

In this lab, you will learn how to create and manage **Apache Iceberg tables** natively within **Google Cloud BigQuery**. 

Unlike standard external tables which are read-only, **BigQuery Managed Iceberg Tables** give you full read-write SQL access. BigQuery handles the metadata and storage optimizations directly in your GCS bucket, allowing you to run `INSERT`, `UPDATE`, and `DELETE` (DML) transactions, and perform **Time Travel** queries to view historical table states.

---

## Complete Chronological Setup & Execution

Follow these steps in order to set up your GCS warehouse, create the BigQuery Connection, assign roles, and run transactions:

### Step 1: Create the GCS Storage Bucket
Open **Cloud Shell** and run the following commands to create a new GCS bucket which will serve as the physical warehouse location for the Iceberg table:

```bash
export PROJECT_ID=your_project_id
export BUCKET_NAME="${PROJECT_ID}-bq-iceberg-warehouse"

# Create a storage bucket in the us-central1 region
gcloud storage buckets create gs://${BUCKET_NAME} --location=us-central1 --project=${PROJECT_ID}
```

---

### Step 2: Create the BigQuery External Connection
To securely read and write GCS files on-the-fly, BigQuery uses an External Connection. 

1. Go to the **BigQuery** console.
2. Open a new **SQL query editor** tab.
3. Run the following statement to create the Connection in the same region:
   ```sql
   CREATE CONNECTION `us-central1.my_gcs_connection`
   OPTIONS (
     connection_type = 'CLOUD_RESOURCE'
   );
   ```
4. In the BigQuery **Explorer** panel on the left, scroll to the bottom, expand **External Connections** ➔ **us-central1**, and click **`my_gcs_connection`**.
5. Copy the **Service Account ID** email address displayed in the connection details (it looks like `bqcx-xxxx@gcp-sa-bigquery-condel.iam.gserviceaccount.com`). You will need this for the next step.

---

### Step 3: Authorize the Connection Service Account on GCS
Now that your connection is created and has a service account, you must grant it permission to read and write files inside your GCS warehouse bucket.

Run the following in **Cloud Shell** (replace `CONNECTION_SA` with the email you copied in Step 2):
```bash
export PROJECT_ID=$(gcloud config get-value project)
export BUCKET_NAME="${PROJECT_ID}-bq-iceberg-warehouse"
export CONNECTION_SA="bqcx-xxxx@gcp-sa-bigquery-condel.iam.gserviceaccount.com"

# Grant Storage permissions to the Connection Service Account
gcloud storage buckets add-iam-policy-binding gs://${BUCKET_NAME} \
  --member="serviceAccount:${CONNECTION_SA}" \
  --role="roles/storage.objectUser"

gcloud storage buckets add-iam-policy-binding gs://${BUCKET_NAME} \
  --member="serviceAccount:${CONNECTION_SA}" \
  --role="roles/storage.legacyBucketReader"
```

---

### Step 4: Grant Project-Level User Roles (If Required)
To ensure your account can run Iceberg queries, grant the necessary BigQuery roles to your logged-in user email.

Run the following in **Cloud Shell** (it will automatically resolve your logged-in account):
```bash
export PROJECT_ID=$(gcloud config get-value project)
export USER_EMAIL=$(gcloud config get-value account)

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

---

### Step 5: Create Dataset and Managed Iceberg Table
Now, return to the **BigQuery SQL Editor** to create your schema dataset and the managed Iceberg table pointing to your GCS warehouse bucket.

1. Create the dataset:
   ```sql
   CREATE SCHEMA `upgradlabs-1750853349290.dataset3`
   OPTIONS (
     location = 'us-central1'
   );
   ```

2. Create the managed Iceberg table (pointing to the bucket created in Step 1):
   ```sql
        CREATE OR REPLACE TABLE dataset3.iceberg_tbl1 (
          device_id STRING,
          date STRING,
          avg_temperature FLOAT64,
          avg_humidity FLOAT64,
          reading_count INT64
      )
      WITH CONNECTION `upgradlabs-1750853349290.us-central1.my_gcs_connection`
      OPTIONS (
        file_format = 'PARQUET',
        table_format = 'ICEBERG',
        storage_uri = 'gs://upgradlabs-1750853349290-iceberg-warehouse/warehouse/iceberg_tbl1'
      );
   ```

---

### Step 6: Run SQL DML Transactions (Insert, Update, Delete)

Run the following statements in the editor to demonstrate write operations:

#### 1. Ingest Data (Insert)
```sql
INSERT INTO dataset3.iceberg_tbl1
(
  device_id,
  date,
  avg_temperature,
  avg_humidity,
  reading_count
)
VALUES
  ('sensor_001', '2026-06-10', 25.5, 60.2, 1440),
  ('sensor_002', '2026-06-10', 27.1, 55.8, 1380),
  ('sensor_003', '2026-06-10', 23.9, 65.1, 1420);
```

#### 2. Verify Ingested Records
```sql
SELECT * FROM dataset3.iceberg_tbl1;
```

#### 3. Modify Records (Update)
```sql
UPDATE dataset3.iceberg_tbl1
SET avg_temperature = 26.8
WHERE device_id = 'sensor_001';
```

#### 4. Drop Records (Delete)
```sql
DELETE FROM dataset3.iceberg_tbl1
WHERE avg_temperature > 30.0;
```

---

### Step 7: Time Travel Queries

Because Iceberg tables track snapshot commits, you can query historical versions of the dataset.

#### 1. Query Current State
Verify the current state of the table (4 rows remain after deleting temperatures above 30):
```sql
SELECT * FROM dataset3.iceberg_tbl1;
```

#### 2. Query Table State in the Past (Time Travel)
Run the following query to view the table's state as of 5 minutes ago (before the update and delete operations):
```sql
SELECT * 
FROM dataset3.iceberg_tbl1 FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE);
```
*Observe that all 5 original rows appear, and the temperature for `sensor_001` returns to its original value (`25.5`), showing that Iceberg successfully traveled back in time!*

---

### Step 8: Cleanup

To delete the resources created in this lab, run the following:
```sql
DROP TABLE IF EXISTS dataset3.iceberg_tbl1;
DROP SCHEMA IF EXISTS dataset3 CASCADE;
```
*(You can also delete `my_gcs_connection` from the External Connections list in the Explorer).*
