# Lab 3: Apache Beam Streaming Pipeline on Google Cloud Dataflow

In this lab you will write a simple **Apache Beam** streaming pipeline using Python and run it on **Google Cloud Dataflow** — Google's fully-managed, serverless data-processing service.

The pipeline performs the following steps:

```
Pub/Sub Input Topic  ──►  Beam Pipeline (UPPERCASE transform)  ──►  Pub/Sub Output Topic
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

## Step 3: Create Pub/Sub Topics and Subscriptions

```bash
# Input topic: where you will publish messages
gcloud pubsub topics create beam-input

# Output topic: where Beam will write transformed messages
gcloud pubsub topics create beam-output

# Subscription to READ results from the output topic
gcloud pubsub subscriptions create beam-output-sub --topic=beam-output
```

---

## Step 4: Create a GCS Bucket for Dataflow Staging

Dataflow needs a Cloud Storage bucket to store temporary files and the pipeline binary.

```bash
export BUCKET_NAME="${PROJECT_ID}-dataflow-temp"

# Create the bucket in your region
gcloud storage buckets create gs://${BUCKET_NAME} \
    --location=${REGION} \
    --project=${PROJECT_ID}
```

---

## Step 5: Clone Lab Files and Install the Beam SDK

```bash
# Navigate to the lab directory (adjust if your path differs)
cd ~/big_data_pipelines_gcp/Lab3

# Install Apache Beam with GCP extras
pip install -r requirements.txt
```

> ⏳ This step installs the full Apache Beam SDK including the Dataflow runner and Pub/Sub client. It may take 2-3 minutes.

---

## Step 6: Submit the Pipeline to Dataflow

Run the following single command to package and submit your pipeline to Dataflow:

```bash
python lab_03_dataflow.py \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --input_topic=projects/${PROJECT_ID}/topics/beam-input \
    --output_topic=projects/${PROJECT_ID}/topics/beam-output \
    --temp_location=gs://${BUCKET_NAME}/temp \
    --staging_location=gs://${BUCKET_NAME}/staging \
    --runner=DataflowRunner \
    --streaming
```

What happens when you run this:
1. Beam packages your Python code and uploads it to the staging GCS bucket.
2. Dataflow provisions worker VMs automatically.
3. The pipeline starts and listens to `beam-input` indefinitely.

> ⏳ The Dataflow job typically takes **2-3 minutes** to start up and show as "Running" in the Console.

---

## Step 7: Monitor the Job in the Dataflow UI

1. Go to [console.cloud.google.com](https://console.cloud.google.com/).
2. Navigate to **Dataflow → Jobs**.
3. Click your running job to see:
   - The **pipeline graph** showing the three steps (Read → Transform → Write).
   - Live **throughput metrics** for each step.
   - Any logs or errors.

---

## Step 8: Test the Pipeline (Send a Message)

Open a **new Cloud Shell tab** and run:

```bash
export PROJECT_ID=$(gcloud config get-value project)

# Publish a test message to the input topic
gcloud pubsub topics publish projects/${PROJECT_ID}/topics/beam-input \
    --message="hello from apache beam"
```

---

## Step 9: Verify the Result (Read from Output)

In another terminal tab, pull a message from the output subscription:

```bash
export PROJECT_ID=$(gcloud config get-value project)

gcloud pubsub subscriptions pull projects/${PROJECT_ID}/subscriptions/beam-output-sub \
    --auto-ack \
    --limit=5
```

You should see the message transformed to **`HELLO FROM APACHE BEAM`** in the `DATA` column!

---

## Step 10: Cleanup

When finished, cancel the Dataflow job to avoid unnecessary charges:

```bash
# List running Dataflow jobs
gcloud dataflow jobs list --region=${REGION} --filter="state=Running"

# Cancel the job (replace JOB_ID with the actual ID from the output above)
gcloud dataflow jobs cancel JOB_ID --region=${REGION}
```

You can also cancel directly from the **Dataflow Jobs** UI in the GCP Console by clicking **Stop** on the job.
