# Lab 2: Spark Structured Streaming with Google Cloud Pub/Sub (Participant Guide)

Welcome to Lab 2! In this lab, you will build a real-time data pipeline using Apache Spark Structured Streaming and Google Cloud Pub/Sub.

You do not need to install anything on your local machine. We will use **Google Cloud Shell**, which comes pre-configured with everything you need, and your pre-provisioned Dataproc cluster.

## Step 1: Open Google Cloud Shell

1. Log in to the [Google Cloud Console](https://console.cloud.google.com/).
2. In the top right corner of the screen, click the **Activate Cloud Shell** icon (it looks like a small `>_` terminal symbol).

![Activate Cloud Shell](/C:/Users/Lenovo/.gemini/antigravity/brain/db610627-6ca3-4884-8389-02e3daefeab3/cloud_shell_btn_1780385426488.png)

A terminal window will open at the bottom of your screen. This is your Cloud Shell environment.

## Step 2: Configure Environment Variables

In your Cloud Shell terminal, run the following commands to automatically detect your Project ID and your Dataproc Cluster details.

```bash
# Automatically fetch your active Google Cloud Project ID
export PROJECT_ID=$(gcloud config get-value project)

# Automatically find the name and region of your Dataproc cluster
export CLUSTER_NAME=$(gcloud dataproc clusters list --format="value(name)" | head -n 1)
export CLUSTER_REGION=$(gcloud dataproc clusters list --format="value(config.gceClusterConfig.zoneUri)" | head -n 1 | awk -F'/' '{print $9}' | awk -F'-' '{print $1"-"$2}')

echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Cluster Region: $CLUSTER_REGION"
```

*(Ensure the echo commands print out actual values for your cluster! If your cluster is missing, ask your instructor.)*

## Step 3: Prepare the Lab Files

Clone the lab files into your Cloud Shell (or navigate to the folder if they are already provided) and install the necessary Python libraries for the mock data generator.

```bash
# Navigate to the lab directory (adjust path if needed)
# cd GCP_Big_Data_Pipelines/Lab2

# Install required python libraries for the publisher
pip install google-cloud-pubsub fastavro
```

## Step 4: Create Pub/Sub Topics

We need two topics: one for raw order data (Avro), and one for processed JSON data.

```bash
# Create the input topic
gcloud pubsub topics create orders-input

# Create the output topic
gcloud pubsub topics create orders-output

# Create a subscription to view the results
gcloud pubsub subscriptions create orders-output-sub --topic=orders-output
```

## Step 5: Start the Data Pipelines

To see the real-time processing in action, we need to run three things simultaneously. We will use `tmux` (Terminal Multiplexer) which is built into Cloud Shell to split our window.

### Split your Cloud Shell Window
1. Open a new Cloud Shell tab by clicking the `+` button in the Cloud Shell toolbar. 
2. Open a *third* tab using the same `+` button. You now have three terminals.

![Split Terminals](/C:/Users/Lenovo/.gemini/antigravity/brain/db610627-6ca3-4884-8389-02e3daefeab3/split_terminals_1780385449951.png)

### Terminal 1: Run the Publisher
In the first tab, start the mock data generator. This will constantly send Avro data to the input topic.
```bash
export PROJECT_ID=$(gcloud config get-value project)
python publisher.py --project_id $PROJECT_ID --topic orders-input
```

### Terminal 2: Run the Consumer
Switch to the second tab. Start the consumer script to listen for the final processed data.
```bash
export PROJECT_ID=$(gcloud config get-value project)
python consumer.py --project_id $PROJECT_ID --subscription orders-output-sub
```
*(This terminal will be quiet until the Spark job begins.)*

### Terminal 3: Submit the Spark Streaming Job
Switch to the third tab. Submit the PySpark job to your Dataproc cluster. We use `--packages` to include the `spark-avro` library so Spark can read the Avro data.

```bash
# Ensure variables are set in this tab
export PROJECT_ID=$(gcloud config get-value project)
export CLUSTER_NAME=$(gcloud dataproc clusters list --format="value(name)" | head -n 1)
export CLUSTER_REGION=$(gcloud dataproc clusters list --format="value(config.gceClusterConfig.zoneUri)" | head -n 1 | awk -F'/' '{print $9}' | awk -F'-' '{print $1"-"$2}')

# Submit the job
gcloud dataproc jobs submit pyspark lab_02_streaming.py \
    --cluster=$CLUSTER_NAME \
    --region=$CLUSTER_REGION \
    --properties=spark.jars.packages=org.apache.spark:spark-avro_2.12:3.3.0 \
    -- $PROJECT_ID orders-input orders-output
```

## Step 6: Verify the Results

Once the Spark job is accepted by the Dataproc cluster and begins processing (this may take 1-2 minutes to spin up the streaming query):

- Look at **Terminal 1**: You will see raw Avro order data being produced.
- Look at **Terminal 2**: You will see the Spark job outputting processed JSON data in real-time, now containing a calculated `total_value` field for every order!

## Cleanup
When finished, press `Ctrl+C` in Terminal 1 and Terminal 2 to stop the python scripts.
You can cancel the Spark streaming job directly from the Dataproc Jobs UI in the Google Cloud Console.
