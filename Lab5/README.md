# Lab 5: End-to-End Apache Iceberg Integration with Beam and Spark

In this lab, you will build an advanced, production-grade streaming and batch architecture. 

1. **Ingestion & Aggregation:** An Apache Beam pipeline on **Google Cloud Dataflow** consumes raw streaming IoT data, groups it in 60-second fixed windows, and writes the aggregate rows directly into an **Apache Iceberg** table on **Google Cloud Storage (GCS)** using a Hadoop Catalog (`org.apache.iceberg.hadoop.HadoopCatalog`).
2. **Batch Processing:** A PySpark program running on **Google Cloud Dataproc** reads the Iceberg table from the staging bucket, processes the data to identify anomalous events (alerts), and writes the processed output to a **new GCS bucket** as a new Iceberg table.

```
+-------------+      Pub/Sub       +---------------------+      GCS Bucket (Staging)      +─────────────────────────+
| publisher.py | ─────────────────> | lab_05_beam_iceberg | ────────────────────────────> | aggregates Table        |
| (IoT Sim)   |     (iot-raw)      | (Fixed Windows 60s) |   gs://STAGE-BUCKET/warehouse   | (Hadoop Iceberg Format)  |
+-------------+                    +---------------------+                                +─────────────────────────+
                                                                                                       │
                                                                                                       ▼ (Spark Reads)
+─────────────────────────+      GCS Bucket (Output)       +────────────────────────────+   +─────────────────────────+
| processed_alerts Table  | <───────────────────────────── | spark_iceberg_processor.py | <─| aggregates Table        |
| (Hadoop Iceberg Format)  |   gs://OUTPUT-BUCKET/warehouse |  (Filters anomalous alerts) |   | (Hadoop Iceberg Format)  |
+─────────────────────────+                                +────────────────────────────+   +─────────────────────────+
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- The following APIs enabled:
  - Cloud Dataflow API
  - Cloud Pub/Sub API
  - Cloud Storage API
  - Cloud Dataproc API
- Access to Cloud Shell (where GCP CLI credentials and SDKs are configured).

---

## Step 1: Open Cloud Shell and Set Environment Variables

Activate Cloud Shell and define your variables. Make sure to choose unique GCS bucket names.

```bash
# Auto-detect your active GCP Project ID
export PROJECT_ID=$(gcloud config get-value project)

# Choose a region (e.g. us-east1 or us-central1)
export REGION=us-east1

# Define staging and output GCS bucket names
export STAGE_BUCKET="${PROJECT_ID}-iceberg-stage"
export OUTPUT_BUCKET="${PROJECT_ID}-iceberg-output"

echo "Project ID     : $PROJECT_ID"
echo "Region         : $REGION"
echo "Staging Bucket : gs://$STAGE_BUCKET"
echo "Output Bucket  : gs://$OUTPUT_BUCKET"
```

---

## Step 2: Enable GCP APIs

```bash
gcloud services enable \
    dataflow.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    dataproc.googleapis.com
```

---

## Step 3: Create Pub/Sub Topic and GCS Buckets

```bash
# Create the input Pub/Sub topic
gcloud pubsub topics create iot-raw

# Create the staging GCS bucket for Beam data staging and the input Iceberg warehouse
gcloud storage buckets create gs://${STAGE_BUCKET} \
    --location=${REGION} \
    --project=${PROJECT_ID}

# Create the final GCS bucket for the processed Iceberg warehouse
gcloud storage buckets create gs://${OUTPUT_BUCKET} \
    --location=${REGION} \
    --project=${PROJECT_ID}
```

---

## Step 4: Install Requirements

Navigate to the `Lab5` directory and install dependencies:

```bash
cd ~/big_data_pipelines_gcp/Lab5

# Install requirements (Beam SDK >= 2.61.0 for Iceberg Managed I/O)
pip install -r requirements.txt
```

---

## Step 5: Start the Telemetry Publisher

Start the simulator script which continuously reads the 1000 records from `sensor_data.csv` and publishes them with updated timestamps to `iot-raw` every `0.5` seconds.

```bash
python publisher.py --project=${PROJECT_ID} --topic=iot-raw --interval=0.5
```

Keep this running and open a **new Cloud Shell tab** for the next steps.

---

## Step 6: Deploy the Beam-to-Iceberg Pipeline on Dataflow

In your second terminal tab, execute the Apache Beam pipeline. The pipeline uses the `beam.managed.Write` connector to write Iceberg data files and metadata directly to GCS.

```bash
cd ~/big_data_pipelines_gcp/Lab5

python lab_05_windowed_beam_iceberg.py \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --input_topic=projects/${PROJECT_ID}/topics/iot-raw \
    --warehouse_path=gs://${STAGE_BUCKET}/warehouse \
    --temp_location=gs://${STAGE_BUCKET}/temp \
    --staging_location=gs://${STAGE_BUCKET}/staging \
    --runner=DataflowRunner \
    --window_duration=60 \
    --streaming
```

---

## Step 7: Verify the Ingested Iceberg Table on GCS

Allow the pipeline to run for 2-3 minutes so that at least two windows materialize. 

Check the warehouse GCS folder to confirm that Iceberg metadata (`.json` files) and data (`.parquet` files) are being created:

```bash
# List files in the Iceberg table folder
gcloud storage ls --recursive gs://${STAGE_BUCKET}/warehouse/sensor_db/aggregates/
```

You should see structures matching:
- `gs://YOUR_STAGING_BUCKET/warehouse/sensor_db/aggregates/metadata/` (snapshots, manifests, table metadata)
- `gs://YOUR_STAGING_BUCKET/warehouse/sensor_db/aggregates/data/` (parquet data files representing window aggregates)

---

## Step 8: Spin up a Dataproc Cluster, Run Spark Job & Jupyter Notebook

We will use Google Cloud Dataproc to run our Spark processing job and run the interactive Jupyter Notebook to demonstrate Time Travel and Schema Evolution.

1. **Create a Dataproc Single Node Cluster with Jupyter & Component Gateway:**
   We configure the cluster with the Iceberg spark runtime package and extensions so that Spark can natively parse Iceberg structures. We also enable Component Gateway and JUPYTER optional component.

   ```bash
   gcloud dataproc clusters create iceberg-processor-cluster \
       --region=${REGION} \
       --single-node \
       --master-machine-type=n2-standard-4 \
       --image-version=2.2-debian12 \
       --optional-components=JUPYTER \
       --enable-component-gateway \
       --properties="spark:spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,spark:spark.jars.packages=org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2" \
       --project=${PROJECT_ID}
   ```

2. **Submit the Batch PySpark Job to Dataproc:**
   Submit the python processor script. The program will load the staging Iceberg tables from `input_cat` (staging GCS bucket), filter for alerts, and write them into `output_cat` (destination GCS bucket).

   ```bash
   gcloud dataproc jobs submit pyspark spark_iceberg_processor.py \
       --cluster=iceberg-processor-cluster \
       --region=${REGION} \
       -- \
       --input_warehouse=gs://${STAGE_BUCKET}/warehouse \
       --output_warehouse=gs://${OUTPUT_BUCKET}/processed_warehouse
   ```

3. **Verify the PySpark Output:**
   In the job outputs, you should see the schema and sample records printed, followed by verification logs. Check that the final Iceberg files are present in the output bucket:
   ```bash
   gcloud storage ls --recursive gs://${OUTPUT_BUCKET}/processed_warehouse/sensor_db/processed_alerts/
   ```

4. **Copy the Jupyter Notebook to GCS Staging for the Cluster:**
   Jupyter on Dataproc automatically loads notebooks stored inside the cluster's default staging bucket in the `notebooks/jupyter/` path.

   ```bash
   # Retrieve the cluster's automatically generated GCS staging bucket name
   export CLUSTER_BUCKET=$(gcloud dataproc clusters describe iceberg-processor-cluster --region=${REGION} --format="value(config.configBucket)")

   # Copy the notebook file to the cluster's notebooks directory on GCS
   gcloud storage cp iceberg_notebook.ipynb gs://${CLUSTER_BUCKET}/notebooks/jupyter/
   ```

5. **Access Jupyter Notebook & Run Time Travel & Schema Evolution Queries:**
   - In the GCP Console, navigate to **Dataproc → Clusters**.
   - Click the name of your cluster (`iceberg-processor-cluster`).
   - Navigate to the **Web Interfaces** tab.
   - Under Component Gateway, click **Jupyter**.
   - The Jupyter tree will load. You will see **`iceberg_notebook.ipynb`** listed.
   - Click to open the notebook, select the **PySpark** kernel, and replace `"gs://YOUR_STAGING_BUCKET/warehouse"` with your actual staging bucket path (e.g. `"gs://YOUR_PROJECT_ID-iceberg-stage/warehouse"`).
   - Execute the cells to see Iceberg's **Time Travel** and **Schema Evolution** queries running in Spark!

---

## Step 9: Cleanup

Once done, tear down the cloud resources to avoid billing:

1. **Stop the Publisher:** Press `Ctrl+C` in the first terminal tab.
2. **Stop the Dataflow Job:**
   ```bash
   gcloud dataflow jobs list --region=${REGION} --filter="state=Running"
   # Cancel using the Job ID:
   gcloud dataflow jobs cancel YOUR_JOB_ID --region=${REGION}
   ```
3. **Delete the Dataproc Cluster:**
   ```bash
   gcloud dataproc clusters delete iceberg-processor-cluster --region=${REGION} --quiet
   ```
4. **Delete Pub/Sub and GCS resources:**
   ```bash
   gcloud pubsub topics delete iot-raw
   gcloud storage buckets delete gs://${STAGE_BUCKET} --recursive
   gcloud storage buckets delete gs://${OUTPUT_BUCKET} --recursive
   ```
