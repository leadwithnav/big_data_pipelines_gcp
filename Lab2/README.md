# Lab 2: Google Cloud Pub/Sub Publisher and Subscriber

In this lab, you will learn how to use the Google Cloud Pub/Sub Python client libraries to create a publisher and subscriber. 

We will use the same IoT telemetry data source as in Lab 4 (`sensor_data.csv` containing 1000 randomized device logs). The publisher reads this file, injects the current UTC timestamp, and publishes it continuously to a Pub/Sub topic. The subscriber listens to a subscription on that topic, receives and prints the messages in real-time, and acknowledges them.

```
+──────────────────────+      Pub/Sub Topic       +─────────────────────+
|     publisher.py     | ───────────────────────> |    subscriber.py    |
| (Reads sensor_data)  |      (lab2-topic)        |   (Logs & Acks)     |
+──────────────────────+                          +─────────────────────+
```

---

## Prerequisites

- A Google Cloud project.
- Cloud Pub/Sub API enabled.
- Access to Cloud Shell.

---

## Step 1: Open Cloud Shell and Set Environment Variables

Activate Cloud Shell (`>_` in the top right of the GCP Console) and set up the project ID:

```bash
# Auto-detect your active GCP Project ID
export PROJECT_ID=<your project id>

echo "Project ID : $PROJECT_ID"
```

---

## Step 2: Enable the Cloud Pub/Sub API

Before running the publisher or subscriber scripts, you must ensure that the Cloud Pub/Sub API is enabled in your Google Cloud project. You can enable it using either of the following methods:

### Method A: Using Cloud Shell (Recommended)
Run the following command in your Cloud Shell terminal to enable the Cloud Pub/Sub API:
```bash
gcloud services enable pubsub.googleapis.com --project=${PROJECT_ID}
```
---

## Step 3: Create Pub/Sub Topic and Subscription

Run the following commands in your Cloud Shell terminal to create the topic and its subscription:

```bash
# Create the Pub/Sub Topic
gcloud pubsub topics create lab2-topic --project=${PROJECT_ID}

# Create a pull subscription bound to the topic
gcloud pubsub subscriptions create lab2-sub --topic=lab2-topic --project=${PROJECT_ID}
```

---

## Step 4: Install Requirements

Navigate to the `Lab2` directory and install the necessary dependencies:

```bash
# Navigate to the Lab 2 directory
cd ~/big_data_pipelines_gcp/Lab2

# Install the google-cloud-pubsub package
pip install -r requirements.txt
```

---

## Step 5: Run the Telemetry Publisher

Start the publisher. It reads the local `sensor_data.csv` (containing randomized device records) and publishes each record directly to `lab2-topic`.

```bash
python publisher.py --project=${PROJECT_ID}
```

You should see logs indicating successful publications:
```
Publishing records from sensor_data.csv to projects/YOUR_PROJECT_ID/topics/lab2-topic...
Published message ID: 10423985020 | Payload: {"device_id": "4", "temperature": "28.5", "humidity": "65.3", "status": "OK"}
Published message ID: 10423985028 | Payload: {"device_id": "2", "temperature": "18.2", "humidity": "45.1", "status": "OK"}
```

Keep this script running. Open a **new Cloud Shell tab/terminal** to execute the subscriber.

---

# Open a New Terminal for Next Step
## Step 6: Run the Telemetry Subscriber

In your second Cloud Shell terminal tab, navigate to the `Lab2` directory and run the subscriber:

```bash
cd ~/big_data_pipelines_gcp/Lab2
export PROJECT_ID=<your project id>
python subscriber.py --project=${PROJECT_ID}
```

Once the subscriber starts, you will see it retrieve and acknowledge the sensor readings published by `publisher.py` in real-time:
```
Listening for messages on projects/YOUR_PROJECT_ID/subscriptions/lab2-sub... Press Ctrl+C to stop.
Received message ID: 10423985020 | Payload: {"device_id": "4", "temperature": "28.5", "humidity": "65.3", "status": "OK"}
Received message ID: 10423985028 | Payload: {"device_id": "2", "temperature": "18.2", "humidity": "45.1", "status": "OK"}
```

---

## Step 7: Cleanup

Once you have verified the publish/subscribe logs, clean up resources to prevent charges:

1. **Stop the Publisher:** Press `Ctrl+C` in the first terminal tab running `publisher.py`.
2. **Stop the Subscriber:** Press `Ctrl+C` in the second terminal tab running `subscriber.py`.
3. **Delete Pub/Sub resources:**
   ```bash
   gcloud pubsub subscriptions delete lab2-sub --project=${PROJECT_ID}
   gcloud pubsub topics delete lab2-topic --project=${PROJECT_ID}
   ```
