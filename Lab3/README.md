# Lab 3: Apache Beam Streaming Pipeline with Apache Iceberg on GCS

In this lab, you will write an **Apache Beam** streaming pipeline using Python, deploy it on **Google Cloud Dataflow**, and ingest live telemetry data from a Pub/Sub topic. The pipeline will filter the sensor data (retaining only clean/OK records) and write the results to a Google Cloud Storage (GCS) bucket in **Apache Iceberg** format using Apache Beam's Managed I/O API.

The architecture performs the following steps:
```
[sensor_data.csv] ──(publisher.py)──► Pub/Sub Topic (beam-input) ──► Beam Pipeline (Filter status=="OK") ──► GCS Bucket (Iceberg Format)
```

---

## Prerequisites

- A Google Cloud project with the following APIs enabled:
  - Cloud Dataflow API
  - Cloud Pub/Sub API
  - Cloud Storage API
- Access to Cloud Shell (all tools are pre-installed)

---

## Step 1: Open Cloud Shell and Set Variables

Click the **Activate Cloud Shell** icon (`>_`) in the top-right of the GCP Console, then run:

```bash
# Auto-detect your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Choose a region (must match where your Dataflow job will run)
export REGION=us-central1

echo "Project : $PROJECT_ID"
echo "Region  : $REGION"
```

---

## Step 2: Enable Required APIs

```bash
gcloud services enable dataflow.googleapis.com pubsub.googleapis.com storage.googleapis.com
```

---

## Step 3: Create Pub/Sub Topic

Create the input topic where the telemetry publisher will stream the simulated sensor data:

```bash
# Input topic: where the publisher will push sensor data
gcloud pubsub topics create beam-input
```

---

## Step 4: Create a GCS Bucket for Iceberg Warehouse and Staging

Dataflow needs a Cloud Storage bucket for temporary staging, and our Iceberg catalog will write data files and metadata directly to this bucket.

```bash
export BUCKET_NAME="${PROJECT_ID}-iceberg-warehouse"

# Create the bucket in your region
gcloud storage buckets create gs://${BUCKET_NAME} \
    --location=${REGION} \
    --project=${PROJECT_ID}
```

---

## Step 5: Install Requirements

Navigate to the Lab 3 directory and install dependencies:

```bash
# Navigate to the lab directory
cd ~/big_data_pipelines_gcp/Lab3

# Install Apache Beam (with GCP and Managed I/O support) and Pub/Sub SDKs
pip install -r requirements.txt
```

---

## Step 6: Deploy the Beam-to-Iceberg Pipeline on Dataflow

Run the following command to package and submit your pipeline to Dataflow. The pipeline will listen to the Pub/Sub topic, filter out records with `status == "ERROR"`, and write clean records into the GCS Iceberg warehouse:

```bash
python lab_03_dataflow.py \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --input_topic=projects/${PROJECT_ID}/topics/beam-input \
    --warehouse_path=gs://${BUCKET_NAME}/warehouse \
    --temp_location=gs://${BUCKET_NAME}/temp \
    --staging_location=gs://${BUCKET_NAME}/staging \
    --runner=DataflowRunner \
    --streaming
```

> ⏳ The Dataflow job typically takes **2-3 minutes** to start up and show as "Running" in the Console.

---

## Step 7: Start the Telemetry Publisher

Open a **new Cloud Shell tab** or terminal, set your variables, and run the publisher script. It reads simulated sensor records from `sensor_data.csv` and streams them into the Pub/Sub topic, injecting the latest UTC timestamp:

```bash
cd ~/big_data_pipelines_gcp/Lab3

export PROJECT_ID=$(gcloud config get-value project)

# Start publishing telemetry every 0.5 seconds
python publisher.py \
    --project=${PROJECT_ID} \
    --topic=beam-input \
    --csv=sensor_data.csv \
    --interval=0.5
```

You should see logs indicating messages are being published.

---

## Step 8: Monitor the Job in the Dataflow UI

1. Go to the GCP Console and search for **Dataflow**.
2. Click on your job to see the live graph:
   - **ReadFromPubSub** ──► **ParseAndFilter** ──► **WriteToIceberg**
3. Verify that the pipeline steps are processing messages.

---

## Step 9: Verify the Generated Output on GCS

Since Apache Iceberg writes data to GCS using a Hadoop catalog layout, you can check that metadata files (`.json`) and data files (`.parquet`) are successfully created under the warehouse path.

Open a terminal and list the contents of your Iceberg table folder:

```bash
export PROJECT_ID=$(gcloud config get-value project)
export BUCKET_NAME="${PROJECT_ID}-iceberg-warehouse"

# List Iceberg table directory recursively
gcloud storage ls --recursive gs://${BUCKET_NAME}/warehouse/sensor_db/filtered_readings/
```

You should see an output structure similar to this:

```
gs://<PROJECT_ID>-iceberg-warehouse/warehouse/sensor_db/filtered_readings/metadata/
gs://<PROJECT_ID>-iceberg-warehouse/warehouse/sensor_db/filtered_readings/metadata/v1.metadata.json
gs://<PROJECT_ID>-iceberg-warehouse/warehouse/sensor_db/filtered_readings/metadata/00000-c9a4058d-7fb4-4a4a-867c-982845c48b29.metadata.json
...
gs://<PROJECT_ID>-iceberg-warehouse/warehouse/sensor_db/filtered_readings/data/
gs://<PROJECT_ID>-iceberg-warehouse/warehouse/sensor_db/filtered_readings/data/00000-0-a4a6011c-2234-45fb-8ba1-cd4981881b29-00001.parquet
```

### Key Iceberg Structure Components:
1. **`metadata/` folder:** Contains `.metadata.json` files which define the table schema, partition specs, and snapshots, along with `.avro` manifest lists.
2. **`data/` folder:** Contains the actual telemetry rows saved in efficient Parquet files.
3. **Filtered records:** Since we filtered out records with `status == "ERROR"`, all Parquet data files will exclusively contain records where `status` is `"OK"`.

---

## Troubleshooting

### Error: "The Dataflow service agent cannot access the worker service account"

To fix this permission issue, run the following commands:

```bash
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")

gcloud iam service-accounts add-iam-policy-binding \
    ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --member="serviceAccount:service-${PROJECT_NUMBER}@dataflow-service-producer-prod.iam.gserviceaccount.com" \
    --role="roles/dataflow.serviceAgent" \
    --project=${PROJECT_ID}
```

---

## Step 10: Cleanup

When finished, stop the Dataflow job and delete resources to avoid incurring charges:

```bash
# Cancel the Dataflow job from terminal (or stop it via the Console UI)
gcloud dataflow jobs list --region=${REGION} --filter="state=Running"

# Cancel using the Job ID returned from the command above
gcloud dataflow jobs cancel JOB_ID --region=${REGION}

# Delete the Pub/Sub input topic
gcloud pubsub topics delete beam-input

# Clean up GCS warehouse bucket
gcloud storage rm -r gs://${BUCKET_NAME}
```
