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
export PROJECT_ID=$(gcloud config get-value project)

echo "Project ID : $PROJECT_ID"
```

---

## Step 2: Install Requirements

Navigate to the `Lab2` directory and install the necessary dependencies:

```bash
# Navigate to the Lab 2 directory
cd ~/big_data_pipelines_gcp/Lab2

# Install the google-cloud-pubsub package
pip install -r requirements.txt
```

---

## Step 3: Run the Telemetry Publisher

Start the publisher. It reads the local `sensor_data.csv` (1000 randomized records of device IDs `1`, `2`, `3`, `4`, `5`), injects the current UTC timestamp, and publishes a message every `0.5` seconds to `lab2-topic`.

*(If the topic does not exist, the script attempts to create it automatically).*

```bash
python publisher.py --project=${PROJECT_ID} --topic=lab2-topic --interval=0.5
```

You should see logs indicating successful publications:
```
2026-06-04 13:10:01 | INFO | Published message ID: 10423985020 | Payload: {"device_id": "4", "temperature": 28.5, "humidity": 65.3, "status": "OK", "timestamp": "2026-06-04T07:40:01.123456+00:00"}
2026-06-04 13:10:02 | INFO | Published message ID: 10423985028 | Payload: {"device_id": "2", "temperature": 18.2, "humidity": 45.1, "status": "OK", "timestamp": "2026-06-04T07:40:01.628901+00:00"}
```

Keep this script running. Open a **new Cloud Shell tab/terminal** to execute the subscriber.

---

## Step 4: Run the Telemetry Subscriber

In your second Cloud Shell terminal tab, navigate to the `Lab2` directory and run the subscriber:

*(If the subscription does not exist, the script attempts to create it automatically and bind it to the topic).*

```bash
cd ~/big_data_pipelines_gcp/Lab2

python subscriber.py --project=${PROJECT_ID} --subscription=lab2-sub --topic=lab2-topic
```

Once the subscriber starts, you will see it retrieve and acknowledge the sensor readings published by `publisher.py` in real-time:
```
2026-06-04 13:10:05 | INFO | Listening for messages on projects/YOUR_PROJECT_ID/subscriptions/lab2-sub... Press Ctrl+C to stop.
2026-06-04 13:10:05 | INFO | Received message ID: 10423985020 | Payload: {"device_id": "4", "temperature": 28.5, "humidity": 65.3, "status": "OK", "timestamp": "2026-06-04T07:40:01.123456+00:00"}
2026-06-04 13:10:05 | INFO | Received message ID: 10423985028 | Payload: {"device_id": "2", "temperature": 18.2, "humidity": 45.1, "status": "OK", "timestamp": "2026-06-04T07:40:01.628901+00:00"}
```

---

## Step 5: Cleanup

Once you have verified the publish/subscribe logs, clean up resources to prevent charges:

1. **Stop the Publisher:** Press `Ctrl+C` in the first terminal tab running `publisher.py`.
2. **Stop the Subscriber:** Press `Ctrl+C` in the second terminal tab running `subscriber.py`.
3. **Delete Pub/Sub resources:**
   ```bash
   gcloud pubsub subscriptions delete lab2-sub
   gcloud pubsub topics delete lab2-topic
   ```
