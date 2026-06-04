# Lab 4: Apache Beam Windowing and Aggregation on Google Cloud Dataflow

In this lab, you will write a production-like **Apache Beam** windowed streaming pipeline in Python and deploy it to **Google Cloud Dataflow**. 

To make this simulation realistic, you will also run a dedicated Python generator script that publishes continuous, real-time IoT sensor telemetry data (temperature, humidity, status) to an ingestion topic. The Beam pipeline will group this data by device, process it in **Fixed Windows**, calculate average metrics, and output the aggregated results back to a Pub/Sub topic.

```
+-------------+      Pub/Sub       +---------------------+      Pub/Sub       +--------------+
| publisher.py | ─────────────────> | lab_04_windowed_beam | ─────────────────> | Verification |
| (IoT Sim)   |     (iot-raw)      | (Fixed Windows 60s) |  (iot-aggregated)  | Subscription |
+-------------+                    +---------------------+                    +--------------+
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- The following APIs enabled:
  - Cloud Dataflow API
  - Cloud Pub/Sub API
  - Cloud Storage API
- Access to Cloud Shell (where tools and credentials are pre-installed).

---

## Step 1: Open Cloud Shell and Set Environment Variables

Activate Cloud Shell (`>_` in the top right of the GCP Console) and set up variables:

```bash
# Auto-detect your active GCP Project ID
export PROJECT_ID=$(gcloud config get-value project)

# Choose a region (e.g. us-east1 or us-central1)
export REGION=us-east1

echo "Project ID : $PROJECT_ID"
echo "Region     : $REGION"
```

---

## Step 2: Enable Required APIs

```bash
gcloud services enable dataflow.googleapis.com pubsub.googleapis.com storage.googleapis.com
```

---

## Step 3: Create Pub/Sub Topics and Subscriptions

We need two topics: one for raw telemetry data input and one for windowed aggregates output. We also need a subscription on the output topic to inspect the results.

```bash
# Create the input topic
gcloud pubsub topics create iot-raw

# Create the output topic
gcloud pubsub topics create iot-aggregated

# Create a subscription to read results from the output topic
gcloud pubsub subscriptions create iot-aggregated-sub --topic=iot-aggregated
```

---

## Step 4: Create a Cloud Storage Bucket

Dataflow uses Cloud Storage to stage temporary binaries and files required to execute your pipeline.

```bash
export BUCKET_NAME="${PROJECT_ID}-dataflow-temp"

# Create a bucket in your chosen region
gcloud storage buckets create gs://${BUCKET_NAME} \
    --location=${REGION} \
    --project=${PROJECT_ID}
```

---

## Step 5: Install Requirements

Navigate to the `Lab4` directory and install the necessary dependencies:

```bash
# Navigate to the Lab 4 directory
cd ~/big_data_pipelines_gcp/Lab4

# Install the dependencies (Beam SDK and Pub/Sub Client)
pip install -r requirements.txt
```

---

## Step 6: Start the Real-Time Publisher

Run the telemetry simulator. It reads sensor records from `sensor_data.csv` (which contains 1,000 randomized records with device IDs `1`, `2`, `3`, `4`, and `5`) and publishes them indefinitely in a loop, injecting the current UTC timestamp into each message.

```bash
python publisher.py --project=${PROJECT_ID} --topic=iot-raw --interval=0.5
```

You should see logs indicating successful publications:
```
2026-06-04 12:40:02 | INFO | Published message ID: 10423984920 | Payload: {"device_id": "3", "temperature": 22.3, "humidity": 44.8, "status": "OK", "timestamp": "2026-06-04T07:10:02.123456+00:00"}
2026-06-04 12:40:02 | INFO | Published message ID: 10423984928 | Payload: {"device_id": "1", "temperature": 27.9, "humidity": 35.1, "status": "OK", "timestamp": "2026-06-04T07:10:02.628901+00:00"}
```

Keep this script running. Open a **new Cloud Shell tab/terminal** to execute the next steps.

---

## Step 7: Deploy the Windowed Beam Pipeline to Dataflow

In your second Cloud Shell tab, run the following command to package and submit your pipeline to Dataflow.

*Note: The `--window_duration` specifies the fixed window size. We will use `60` seconds.*

```bash
cd ~/big_data_pipelines_gcp/Lab4

python lab_04_windowed_beam.py \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --input_topic=projects/${PROJECT_ID}/topics/iot-raw \
    --output_topic=projects/${PROJECT_ID}/topics/iot-aggregated \
    --temp_location=gs://${BUCKET_NAME}/temp \
    --staging_location=gs://${BUCKET_NAME}/staging \
    --runner=DataflowRunner \
    --window_duration=60 \
    --streaming
```

> 💡 **Troubleshooting: ZONE_RESOURCE_POOL_EXHAUSTED**
> If your worker pool startup fails due to Compute Engine stockouts in your default zone, you can append `--worker_zone=us-east1-b` (or another zone matching your region) to force VM creation in a specific zone.

---

## Step 8: Monitor the Dataflow Job

1. Open the [GCP Console](https://console.cloud.google.com).
2. Go to **Dataflow → Jobs**.
3. Select your job (usually starts with `beamapp-...`).
4. Watch the pipeline graph construct. Since this is a streaming pipeline, it will keep running indefinitely with steps:
   - `ReadFromPubSub`
   - `ParseAndTimestamp`
   - `ApplyFixedWindows`
   - `GroupPerDevice`
   - `AggregateTelemetry`
   - `WriteToPubSub`

---

## Step 9: Verify the Windowed Aggregation Results

Once the Dataflow job status turns green/Running, open a third terminal tab or wait 1-2 minutes for the first window to materialize. Run the following command to pull and display aggregated records from the output subscription:

```bash
export PROJECT_ID=$(gcloud config get-value project)

gcloud pubsub subscriptions pull projects/${PROJECT_ID}/subscriptions/iot-aggregated-sub \
    --auto-ack \
    --limit=3
```

You should see output similar to this:
```json
{
  "device_id": "3",
  "window_start": "2026-06-04T07:10:00Z",
  "window_end": "2026-06-04T07:11:00Z",
  "avg_temperature": 24.58,
  "avg_humidity": 51.12,
  "reading_count": 42,
  "error_count": 2,
  "aggregated_at": "2026-06-04T07:11:05.124536Z"
}
```

Observe that:
- Averages are calculated per `device_id` (e.g. `3`).
- The window start and end times correspond to exact 60-second boundaries (e.g., `07:10:00` to `07:11:00`).
- The reading count matches the number of messages published by the simulator for that device during that specific 1-minute window.

---

## Step 10: Cleanup

Once you have verified the results, clean up resources to prevent charges:

1. **Stop the Publisher:** Press `Ctrl+C` in the first terminal tab running `publisher.py`.
2. **Stop the Dataflow Job:** Cancel the job via the Dataflow Console UI (click **Stop → Cancel**) or from the command line:
   ```bash
   gcloud dataflow jobs list --region=${REGION} --filter="state=Running"
   # Copy the JOB_ID from above and run:
   gcloud dataflow jobs cancel YOUR_JOB_ID --region=${REGION}
   ```
3. **Delete Pub/Sub resources:**
   ```bash
   gcloud pubsub subscriptions delete iot-aggregated-sub
   gcloud pubsub topics delete iot-raw
   gcloud pubsub topics delete iot-aggregated
   ```
4. **Delete Cloud Storage bucket:**
   ```bash
   gcloud storage buckets delete gs://${BUCKET_NAME} --recursive
   ```
