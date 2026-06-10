# Lab 6: BigQuery Data Lakes — External Tables and Table Optimizations

In this lab, you will explore **Google Cloud BigQuery** in a hybrid data lake architecture:
1. **BigQuery Dataset Creation:** Establishing a logical container for database structures.
2. **External Tables:** Querying files directly in **Google Cloud Storage (GCS)** without loading them into BigQuery native storage (zero-copy query).
3. **Table Optimizations (Partitioning and Clustering):** Loading data into native optimized storage using:
   - **Partitioning:** Segmenting the table by day (`timestamp`) to enable partition pruning (scanning only required days).
   - **Clustering:** Ordering data within partitions by specified keys (`device_id`) to accelerate filter and aggregation performance.

```
┌─────────────────────────────────────────────────────────────────────────────+
│                           BIGQUERY DATA LAKE & WAREHOUSE                    │
│                                                                             │
│   GCS CSV File (Cloud Storage)                BigQuery External Table       │
│  [ gs://my-bucket/sensor_data.csv ]  ──────>  [ external_sensor_data ]      │
│                                                          │                  │
│                                                (SQL queries directly on GCS)│
│                                                          │                  │
│                                                          ▼                  │
│                                               Native Optimized Table        │
│                                              [ partitioned_clustered_telemetry ]
│                                              - Partitioned by Date(timestamp)│
│                                              - Clustered by device_id       │
└─────────────────────────────────────────────────────────────────────────────+
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- Access to Cloud Shell.
- A Cloud Storage bucket (e.g. `YOUR_PROJECT_ID-dataflow-temp` created in previous labs).

---

## Step 1: Open Cloud Shell and Copy Dataset to GCS

We will copy the local `sensor_data.csv` to our GCS bucket to act as the raw data source for our external table.

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

1. In the GCP Console, search for and navigate to **BigQuery**.
2. Open a new **SQL query editor** tab.
3. Run the following DDL statement to create a dataset `sensor_analytics`:
   ```sql
   CREATE SCHEMA IF NOT EXISTS `sensor_analytics` 
   OPTIONS(location="us-east1");
   ```
   *Verify that `sensor_analytics` appears in the Explorer panel on the left.*

---

## Step 3: Create a BigQuery External Table Over GCS

We will define an external table that references the CSV file on Cloud Storage directly. Queries against this table will read GCS storage on-the-fly.

1. Run the following query in the editor (replace `YOUR_PROJECT_ID` with your actual GCP Project ID):
   ```sql
   CREATE OR REPLACE EXTERNAL TABLE `sensor_analytics.external_sensor_data` (
     device_id STRING,
     temperature FLOAT64,
     humidity FLOAT64,
     status STRING
   )
   OPTIONS (
     format = 'CSV',
     uris = ['gs://YOUR_PROJECT_ID-dataflow-temp/sensor_data.csv'],
     skip_leading_rows = 1
   );
   ```

---

## Step 4: Run SQL Queries on the External Table (Directly Querying GCS)

You can now run standard SQL queries to analyze files stored in GCS.

### Query 1: Total Records Count
Verify that BigQuery can read all rows from the raw GCS CSV:
```sql
SELECT COUNT(*) as total_records FROM `sensor_analytics.external_sensor_data`;
```

### Query 2: Filter Anomalous Readings
Select records where status is not normal:
```sql
SELECT * 
FROM `sensor_analytics.external_sensor_data` 
WHERE status != 'OK' 
LIMIT 10;
```

### Query 3: Statistical Summary grouped by Device
Aggregate temperature and humidity measurements:
```sql
SELECT 
  device_id, 
  ROUND(AVG(temperature), 2) as avg_temp,
  ROUND(MIN(temperature), 2) as min_temp,
  ROUND(MAX(temperature), 2) as max_temp,
  ROUND(AVG(humidity), 2) as avg_humidity
FROM 
  `sensor_analytics.external_sensor_data`
GROUP BY 
  device_id
ORDER BY 
  avg_temp DESC;
```

---

## Step 5: Ingest and Optimize GCS Data into a Partitioned and Clustered Native Table

While external tables are highly convenient, native optimized tables offer significantly better performance for analytical workloads. You can create a native table that is **partitioned by timestamp** and **clustered by device_id** using either of the following two methods:

### Method A: Separate Table Definition and Ingestion (DDL + INSERT)
This is the standard approach when you need to define a table schema upfront (e.g. for streaming or scheduled writes).

1. Define the empty partitioned & clustered table structure:
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

2. Populate the table by selecting data from the GCS external table (generating randomized timestamps over the last 5 days):
   ```sql
   INSERT INTO `sensor_analytics.partitioned_clustered_telemetry` (device_id, temperature, humidity, status, timestamp)
   SELECT 
     device_id, 
     temperature, 
     humidity, 
     status, 
     -- Randomly distribute timestamps over the last 5 days
     TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL CAST(RAND() * 5 AS INT64) DAY) as timestamp
   FROM `sensor_analytics.external_sensor_data`;
   ```

### Method B: Single-Step Ingestion and Table Creation (CTAS - Create Table As Select)
This method creates the table, defines partitioning and clustering, and loads the data from GCS in a single SQL execution.

Run the following query:
```sql
CREATE OR REPLACE TABLE `sensor_analytics.partitioned_clustered_telemetry`
PARTITION BY DATE(timestamp)
CLUSTER BY device_id
AS
SELECT 
  device_id, 
  temperature, 
  humidity, 
  status, 
  -- Randomly distribute timestamps over the last 5 days
  TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL CAST(RAND() * 5 AS INT64) DAY) as timestamp
FROM `sensor_analytics.external_sensor_data`;
```

---

## Step 6: Compare Query Performance (Data Lake vs. Optimized Warehouse)

Run comparison queries. Do not run them immediately; look at the **query validator indicator** (green checkmark) in the top-right corner of the editor to inspect the **estimated bytes to be processed**.

### Comparison 1: Querying Raw GCS Data (External Table)
```sql
SELECT AVG(temperature) as avg_temp 
FROM `sensor_analytics.external_sensor_data` 
WHERE device_id = '3';
```
- **Estimated Bytes:** BigQuery must scan the *entire CSV file* on GCS because external text formats do not support indexing, partition pruning, or clustering metadata.

### Comparison 2: Querying Optimized Native Table (Partitioning & Clustering)
```sql
SELECT AVG(temperature) as avg_temp
FROM `sensor_analytics.partitioned_clustered_telemetry`
WHERE DATE(timestamp) = CURRENT_DATE() AND device_id = '3';
```
- **Estimated Bytes:** BigQuery uses **partition pruning** to read only the partition folder for `CURRENT_DATE()`, and uses **clustering metadata** to skip directly to blocks containing `device_id = '3'`. The scanned bytes will be a tiny fraction of the first query.

---

## Step 7: Cleanup

Delete the dataset and tables created in this lab to avoid ongoing storage costs:

```sql
DROP TABLE IF EXISTS `sensor_analytics.partitioned_clustered_telemetry`;
DROP TABLE IF EXISTS `sensor_analytics.external_sensor_data`;
DROP SCHEMA IF EXISTS `sensor_analytics` CASCADE;
```
