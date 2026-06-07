# Lab 6: BigQuery Table Optimization: Partitioning and Clustering

In this lab, you will learn how to optimize query performance and reduce query costs in **Google Cloud BigQuery** using two powerful techniques:
1. **Partitioning:** Splitting a table into smaller segments based on a date or timestamp column. BigQuery will only scan the partitions that match your filter (known as **partition pruning**).
2. **Clustering:** Sorting and organizing the data within each partition based on the values of one or more columns (e.g. `device_id`). This makes queries with filters or aggregations on the clustered columns faster and cheaper.

You will load the telemetry dataset `sensor_data.csv` from Cloud Storage, distribute the records across multiple daily partitions, and run comparison queries to measure the performance gains in the BigQuery Web UI.

```
+─────────────────────────────────────────────────────────────────────────────+
|                                  BigQuery                                   |
|                                                                             |
|   +─────────────────────────────────────────────────────────────────────+   |
|   |         partitioned_clustered_telemetry Table                       |   |
|   |                                                                     |   |
|   |   Partitioned by DATE(timestamp) (Daily buckets)                    |   |
|   |   +─────────────────+─────────────────+─────────────────+           |   |
|   |   |   2026-06-01    |   2026-06-02    |   2026-06-03    | ...       |   |
|   |   |  (device_id 1)  |  (device_id 1)  |  (device_id 1)  |           |   |
|   |   |  (device_id 2)  |  (device_id 2)  |  (device_id 2)  |           |   |
|   |   +─────────────────+─────────────────+─────────────────+           |   |
|   |   * Clustered inside each partition by device_id                     |   |
|   +─────────────────────────────────────────────────────────────────────+   |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## Prerequisites

- A Google Cloud project.
- Access to Cloud Shell.
- A Cloud Storage bucket (e.g. `YOUR_PROJECT_ID-dataflow-temp` created in previous labs).

---

## Step 1: Open Cloud Shell and Copy Dataset to GCS

We need to upload our local `sensor_data.csv` to a GCS bucket so that BigQuery can load it.

1. Activate Cloud Shell (`>_` in the top right of the GCP Console).
2. Set environment variables and copy the CSV:
   ```bash
   # Set variables
   export PROJECT_ID=$(gcloud config get-value project)
   export BUCKET_NAME="${PROJECT_ID}-dataflow-temp"

   # Navigate to Lab 6 directory
   cd ~/big_data_pipelines_gcp/Lab6

   # Copy the local CSV template to your GCS bucket
   gcloud storage cp sensor_data.csv gs://${BUCKET_NAME}/
   ```

---

## Step 2: Open BigQuery SQL Editor and Create Dataset

1. In the GCP Console, navigate to **BigQuery**.
2. Open a new **SQL query editor** tab.
3. Run the following DDL statement to create a dataset `sensor_analytics`:
   ```sql
   CREATE SCHEMA IF NOT EXISTS `sensor_analytics` 
   OPTIONS(location="us-east1");
   ```

---

## Step 3: Define a Partitioned and Clustered Table

We will create a target table partitioned by the `timestamp` column (truncated to the day) and clustered by `device_id`.

Run the following query in the editor:
```sql
CREATE OR REPLACE TABLE `sensor_analytics.partitioned_clustered_telemetry` (
  device_id STRING,
  temperature FLOAT64,
  humidity FLOAT64,
  status STRING,
  timestamp TIMESTAMP
)
PARTITION BY DATE(timestamp)
CLUSTER BY device_id;
```

---

## Step 4: Load GCS Data into a Staging Table

To simulate a real dataset distributed over time, we will load the raw GCS CSV into a temporary staging table first, and then insert it into our optimized table.

1. Run the DDL query to create a temporary table and load the CSV from GCS using the SQL `LOAD DATA` command (replace `YOUR_PROJECT_ID` with your actual project ID):
   ```sql
   CREATE OR REPLACE TEMP TABLE `staging_telemetry` (
     device_id STRING,
     temperature FLOAT64,
     humidity FLOAT64,
     status STRING
   );

   LOAD DATA OVERWRITE `staging_telemetry`
   FROM FILES (
     format = 'CSV',
     uris = ['gs://YOUR_PROJECT_ID-dataflow-temp/sensor_data.csv'],
     skip_leading_rows = 1
   );
   ```

---

## Step 5: Populate Partitioned Table with Randomized Timestamps

Since `sensor_data.csv` does not contain a timestamp column, we will insert the records into our target partitioned table and distribute the timestamps randomly over the last 5 days. This will populate multiple distinct daily partitions.

Run the following query:
```sql
INSERT INTO `sensor_analytics.partitioned_clustered_telemetry` (device_id, temperature, humidity, status, timestamp)
SELECT 
  device_id, 
  temperature, 
  humidity, 
  status, 
  -- Randomly distribute timestamps over the last 5 days
  TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL CAST(RAND() * 5 AS INT64) DAY) as timestamp
FROM `staging_telemetry`;
```

---

## Step 6: Verify Partition Pruning and Clustering in BigQuery UI

Now we will run comparison queries. For each query, **do not run it immediately**. Look at the **query validator indicator** (green checkmark) in the top-right corner of the SQL Editor to see the estimated **Bytes to be processed**.

### Query 1: Full Table Scan (No Filters)
This query scans every partition and every column:
```sql
SELECT * FROM `sensor_analytics.partitioned_clustered_telemetry`;
```
*Observe the estimated bytes processed. It represents the full size of the table.*

### Query 2: Filter by Partition (Partition Pruning)
This query filters by the partition column `timestamp`. BigQuery will only scan the data in the partition of the specified date:
```sql
SELECT * 
FROM `sensor_analytics.partitioned_clustered_telemetry`
WHERE DATE(timestamp) = CURRENT_DATE();
```
*Observe the estimated bytes processed. It will be roughly **1/5th** (20%) of the full table scan size, demonstrating partition pruning!*

### Query 3: Filter by Partition and Cluster Column
This query filters by the partition date and further filters by the clustered column `device_id`. BigQuery uses clustering metadata to jump directly to blocks containing `device_id = '3'` within that partition:
```sql
SELECT AVG(temperature) as avg_temp
FROM `sensor_analytics.partitioned_clustered_telemetry`
WHERE DATE(timestamp) = CURRENT_DATE() AND device_id = '3';
```
*Observe the estimated bytes. Because we only aggregate `temperature` and filter on the clustered key, the bytes scanned are reduced even further!*

---

## Step 7: Cleanup

Run the following statements to delete the resources created in this lab:

```sql
DROP TABLE IF EXISTS `sensor_analytics.partitioned_clustered_telemetry`;
DROP SCHEMA IF EXISTS `sensor_analytics` CASCADE;
```
