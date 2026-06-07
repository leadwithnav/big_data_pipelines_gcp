# Lab 6: BigQuery Managed Iceberg Tables

In this lab, you will learn how to create and manage **Apache Iceberg tables** natively within **Google Cloud BigQuery**. 

Rather than setting up an external metastore or manually syncing metadata JSON files (as with read-only external tables), you will use **BigQuery Managed Iceberg Tables**. This feature allows BigQuery to handle the metadata and storage optimizations (like manifest management and snapshot tracking) directly in your Google Cloud Storage (GCS) bucket, enabling full read-write SQL access (such as running `INSERT` or `SELECT` statements).

```
+───────────────────────────+
|     BigQuery Console      |
|                           |
|    [ SQL Workspace ]      |
|    - Create Connection    |
|    - CREATE TABLE DDL     |
|    - INSERT DML Query     |
|    - SELECT SQL Query     |
+───────────────────────────+
              │
              ▼ (Read/Write access via Connection Service Account)
+───────────────────────────────────────────────────────────+
|               Google Cloud Storage (GCS)                  |
|                                                           |
|    - gs://STAGE-BUCKET/managed_warehouse/                 |
|      - /metadata/ (BigQuery-managed manifests & snapshots)|
|      - /data/ (Parquet data files)                        |
+───────────────────────────────────────────────────────────+
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- The BigQuery Connection API enabled.
- A Cloud Storage bucket to act as the warehouse (e.g. your staging bucket `YOUR_PROJECT_ID-iceberg-stage` created in Lab 5).

---

## Phase 1: Create an External Connection in the BigQuery UI

BigQuery uses a **Cloud Resource Connection** to securely access your Cloud Storage bucket to write and read Iceberg data files.

1. Open the [GCP Console](https://console.cloud.google.com).
2. Navigate to **BigQuery** to open the Web UI.
3. In the **Explorer** panel on the left, click **+ ADD** and select **Connections to external data sources**.
4. In the External connection creation pane, enter the following details:
   - **Connection type:** Select `BigLake and remote functions (Cloud Resource)`.
   - **Connection ID:** Enter `my-gcs-connection`.
   - **Connection region:** Select `us-east1` (or whichever region matches your GCS staging bucket).
5. Click **Create connection**.
6. In the Explorer panel, expand **External Connections** at the bottom, select your newly created connection, and copy the **Service Account ID** email address (e.g., `bqcx-123456789-abcd@gcp-sa-bigquery-condel.iam.gserviceaccount.com`) from the connection details.

---

## Phase 2: Set up IAM Permissions via the GCS Console

Since BigQuery needs to write data and metadata files to GCS for managed tables, you must grant the connection's service account permission to create and delete objects.

1. Navigate to the **Cloud Storage** browser.
2. Select your staging bucket (e.g., `YOUR_PROJECT_ID-iceberg-stage`).
3. Click on the **Permissions** tab and click **Grant Access**.
4. In the **New Principals** field, paste the **Service Account ID** email address you copied in Phase 1.
5. In the **Select a role** dropdown, choose `Cloud Storage` -> `Storage Object Admin`.
   *(Storage Object Admin is required because BigQuery must write data, write manifests, and update metadata files).*
6. Click **Save**.

---

## Phase 3: Create Dataset and Managed Iceberg Table in BigQuery UI

We will run SQL statements inside the BigQuery SQL Workspace to register our managed Iceberg table on GCS.

1. In the **BigQuery Console**, open a new **SQL query editor** tab.
2. Run the following DDL query to create a dataset:
   ```sql
   CREATE SCHEMA IF NOT EXISTS `sensor_analytics` 
   OPTIONS(location="us-east1");
   ```
3. Run the DDL query to create the managed Iceberg table, replacing `YOUR_PROJECT_ID` and the GCS URI with your actual details:
   ```sql
   CREATE OR REPLACE TABLE `sensor_analytics.managed_aggregates` (
     device_id STRING,
     avg_temperature DOUBLE,
     avg_humidity DOUBLE,
     reading_count INT64,
     error_count INT64,
     aggregated_at STRING
   )
   WITH CONNECTION `YOUR_PROJECT_ID.us-east1.my-gcs-connection`
   OPTIONS (
     file_format = 'PARQUET',
     table_format = 'ICEBERG',
     storage_uri = 'gs://YOUR_PROJECT_ID-iceberg-stage/managed_warehouse/'
   );
   ```
4. Once the query executes successfully, expand your `sensor_analytics` dataset in the Explorer panel and click the `managed_aggregates` table. Navigate to the **Details** tab and verify the table format is listed as **ICEBERG**.

---

## Phase 4: Run SQL Queries and DML inside BigQuery UI

Now you can interact with the table. Unlike external read-only tables, you can run `INSERT`, `UPDATE`, and `DELETE` queries.

### Query 1: Insert Records (DML)
Insert dummy telemetry aggregate records into the Iceberg table:
```sql
INSERT INTO `sensor_analytics.managed_aggregates` (device_id, avg_temperature, avg_humidity, reading_count, error_count, aggregated_at)
VALUES 
  ('1', 24.58, 51.12, 42, 2, '2026-06-04T07:11:05.124536Z'),
  ('2', 19.34, 45.89, 38, 0, '2026-06-04T07:11:05.124536Z'),
  ('3', 28.12, 33.45, 51, 1, '2026-06-04T07:11:05.124536Z');
```

### Query 2: Read Records
Query the table to read the inserted records:
```sql
SELECT * FROM `sensor_analytics.managed_aggregates`;
```

### Query 3: Analyze the Underlying Storage
In your Cloud Storage browser, open the staging bucket and navigate to `managed_warehouse/`. You will see:
- `/data/` containing the Parquet data files created by BigQuery.
- `/metadata/` containing the Iceberg metadata, manifest lists, and manifest files created by BigQuery during the transaction.

*Since it is in standard Iceberg format, other engines like Apache Spark or Trino can read this table directly from your GCS bucket!*

---

## Phase 5: Cleanup

To clean up resources:

1. **Delete the BigQuery table and dataset:**
   Run the following query in the SQL Editor:
   ```sql
   DROP TABLE IF EXISTS `sensor_analytics.managed_aggregates`;
   DROP SCHEMA IF EXISTS `sensor_analytics` CASCADE;
   ```
2. **Delete the Connection:**
   In the Explorer panel under **External Connections**, click your connection (`my-gcs-connection`), and click **Delete connection** in the details tab.
