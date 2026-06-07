# Lab 0: Exploring Dataproc, YARN, and HDFS

In this introductory lab, you will get hands-on experience with the core components of a managed Hadoop ecosystem on Google Cloud Platform:
1. **Google Cloud Dataproc:** GCP's fully-managed Apache Spark and Apache Hadoop service.
2. **Hadoop Distributed File System (HDFS):** The standard distributed storage layer where you will load and read telemetry data using the `hdfs dfs` CLI.
3. **YARN (Yet Another Resource Negotiator):** The cluster resource manager and job scheduler. You will submit a PySpark application and inspect how YARN schedules and manages it via the **YARN Resource Manager UI**.

```
+─────────────────────────────────────────────────────────────────────────────+
|                          Google Cloud Dataproc                              |
|                                                                             |
|   +───────────────────────────────+      YARN Resource Manager UI           |
|   |         HDFS Storage          |      - Tracks Spark Application         |
|   |   - /user/telemetry/          |      - Displays memory/CPU containers   |
|   |     (sensor_data.csv)         |      - Access logs in real-time         |
|   +───────────────────────────────+                                         |
|                   ▲                                                         |
|                   │ (Spark Reads & Writes)                                  |
|   +───────────────────────────────+                                         |
|   |        pyspark_job.py         |                                         |
|   |   (Aggregations per device)   |                                         |
|   +───────────────────────────────+                                         |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- Dataproc and Compute Engine APIs enabled.
- Access to Cloud Shell.

---

## Step 1: Open Cloud Shell and Set Environment Variables

Activate Cloud Shell (`>_` in the top right of the GCP Console) and set up the cluster and region variables:

```bash
# Auto-detect your active GCP Project ID
export PROJECT_ID=$(gcloud config get-value project)

# Choose a region (e.g. us-east1 or us-central1)
export REGION=us-east1

# Define your cluster name
export CLUSTER_NAME="lab0-dataproc-cluster"

echo "Project ID   : $PROJECT_ID"
echo "Region       : $REGION"
echo "Cluster Name : $CLUSTER_NAME"
```

---

## Step 2: Create a Dataproc Cluster

Create a cost-effective single-node cluster. We explicitly enable **Component Gateway** to allow secure web access to YARN and other Hadoop UIs directly from our browser.

```bash
gcloud dataproc clusters create ${CLUSTER_NAME} \
    --region=${REGION} \
    --single-node \
    --master-machine-type=n2-standard-4 \
    --image-version=2.2-debian12 \
    --enable-component-gateway \
    --project=${PROJECT_ID}
```

---

## Step 3: Copy Telemetry Dataset to the Master Node

To load files into HDFS, we must first copy our dataset to the master node's filesystem. From your local Cloud Shell terminal, run:

```bash
# Verify you are in the Lab0 folder
cd ~/big_data_pipelines_gcp/Lab0

# SCP the local sensor_data.csv to the master VM's home directory
gcloud compute scp sensor_data.csv ${CLUSTER_NAME}-m:~ \
    --zone=${REGION}-b \
    --project=${PROJECT_ID}
```

---

## Step 4: SSH into Master Node & Run HDFS Commands

SSH into the cluster's master node to access the HDFS command-line interface.

1. **SSH Connection:**
   ```bash
   gcloud compute ssh ${CLUSTER_NAME}-m \
       --zone=${REGION}-b \
       --project=${PROJECT_ID}
   ```
   *(Accept prompt to generate SSH keys if this is your first connection).*

2. **Run HDFS commands:**
   Use the Hadoop FS shell utility (`hdfs dfs`) to interact with HDFS:

   ```bash
   # A. Create a directory in HDFS for raw telemetry data
   hdfs dfs -mkdir -p /user/telemetry
   
   # B. Copy the dataset from master node local disk to HDFS
   hdfs dfs -put ~/sensor_data.csv /user/telemetry/
   
   # C. List the contents of the HDFS directory to verify upload
   hdfs dfs -ls /user/telemetry/
   
   # D. Read the first 10 lines of the file inside HDFS
   hdfs dfs -cat /user/telemetry/sensor_data.csv | head -n 10
   ```

Keep this SSH terminal open. Open a **new Cloud Shell tab** to submit your Spark job.

---

## Step 5: Submit PySpark Job to the YARN Scheduler

In your new Cloud Shell tab, navigate to the lab directory and submit the PySpark job to your cluster:

```bash
cd ~/big_data_pipelines_gcp/Lab0

gcloud dataproc jobs submit pyspark pyspark_job.py \
    --cluster=${CLUSTER_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    -- \
    --input=hdfs:///user/telemetry/sensor_data.csv \
    --output=hdfs:///user/telemetry/output
```

YARN will negotiate resources, allocate containers on the master node, schedule tasks, and process the HDFS input file. The aggregation output (record counts and averages grouped by device ID) will print directly to the job log.

---

## Step 6: Explore the YARN Resource Manager UI

Thanks to Component Gateway, you can explore the YARN ResourceManager web panel:

1. Open the [GCP Console](https://console.cloud.google.com).
2. Navigate to **Dataproc → Clusters**.
3. Click on your running cluster: **`lab0-dataproc-cluster`**.
4. Go to the **Web Interfaces** tab.
5. Click the link for **YARN ResourceManager**.
6. The dashboard will load. Under **Applications**, you can see:
   - Your completed PySpark job (`Lab0-HDFS-Telemetry-Aggregator`).
   - The status of allocated Vcores, Containers, and Memory.
   - Click the **History** or **Logs** links to see job logs captured by YARN.

---

## Step 7: Verify Results in HDFS

Return to your **Master Node SSH terminal** (Step 4) and list/read the output created by Spark in HDFS:

```bash
# List output files generated by Spark in HDFS
hdfs dfs -ls /user/telemetry/output/

# Read the aggregated CSV results
hdfs dfs -cat /user/telemetry/output/*.csv
```

---

## Step 8: Cleanup

When finished, delete the Dataproc cluster to avoid charges:

```bash
# In your Cloud Shell terminal
gcloud dataproc clusters delete ${CLUSTER_NAME} --region=${REGION} --quiet
```
