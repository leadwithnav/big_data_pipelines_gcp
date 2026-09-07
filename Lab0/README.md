# Lab 0: Google Cloud Dataproc and YARN Exploration

In this introductory lab, you will get hands-on experience with:
1. **Google Cloud Dataproc:** GCP's fully-managed Apache Spark and Apache Hadoop service.
2. **YARN (Yet Another Resource Negotiator):** The cluster resource manager and job scheduler. You will submit a Spark application and inspect how YARN schedules and manages it via the **YARN Resource Manager UI**.

```
+─────────────────────────────────────────────────────────────────────────────+
|                          Google Cloud Dataproc                              |
|                                                                             |
|   +───────────────────────────────+      YARN Resource Manager UI           |
|   |         Cloud Shell           |      - Tracks Spark Application         |
|   |   - Submits Spark job        | ───> - Displays memory/CPU containers   |
|   |     (Spark Pi Example)        |      - Access logs in real-time         |
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

# Choose a region and zone (e.g. us-central1 / us-central1-a)
export REGION=us-central1
export ZONE=us-central1-a

# Define your cluster name
export CLUSTER_NAME="cluster-lab"

echo "Project ID   : $PROJECT_ID"
echo "Region       : $REGION"
echo "Zone         : $ZONE"
echo "Cluster Name : $CLUSTER_NAME"
```

```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```
---

---

## Step 4: Create a Dataproc Cluster

Create a cost-effective single-node cluster. We explicitly enable **Component Gateway** to allow secure web access to YARN and other Hadoop UIs directly from our browser.

> ⏳ **Note:** Creating the Dataproc cluster typically takes **5 to 7 minutes** to complete as it provisions the VM instances, installs the Hadoop ecosystem, and configures cluster software.

```bash
gcloud dataproc clusters create ${CLUSTER_NAME} \
    --region=${REGION} \
    --zone=${ZONE} \
    --single-node \
    --master-machine-type=n2-standard-4 \
    --image-version=2.2-debian12 \
    --enable-component-gateway \
    --optional-components=JUPYTER \
    --project=${PROJECT_ID}
```

---

## Step 5: Open the YARN Resource Manager UI

Thanks to Component Gateway, you can explore the YARN ResourceManager web panel securely without setting up SSH tunnels:

1. Open the [GCP Console](https://console.cloud.google.com).
2. Navigate to **Dataproc → Clusters**.
3. Click on your running cluster: **`lab0-dataproc-cluster`**.
4. Go to the **Web Interfaces** tab.
5. Click the link for **YARN ResourceManager**.
6. The dashboard will load showing 0 active or completed applications. Keep this tab open.

---

## Step 6: Submit a Spark Job from the Cloud Shell Terminal

Return to your Cloud Shell terminal and run the following command to submit a Spark job. We will use a pre-packaged built-in **Spark Pi** example jar located on the cluster master VM to calculate Pi:

```bash
gcloud dataproc jobs submit spark \
    --cluster=${CLUSTER_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --class=org.apache.spark.examples.SparkPi \
    --jars=file:///usr/lib/spark/examples/jars/spark-examples.jar \
    -- 1000
```

This submits the application to the Dataproc master node, which delegates the job execution to YARN.

---

## Step 7: Verify the Application on YARN UI & Dataproc Jobs CLI

1. Switch back to your **YARN ResourceManager** browser tab (opened in Step 5).
2. Refresh the page. You should now see the active Spark application running under the name:
   `org.apache.spark.examples.SparkPi`
3. Check the application state as it transitions from `ACCEPTED` to `RUNNING`, and finally to `FINISHED` (usually takes 30-45 seconds).
4. Inspect the application statistics:
   - Click the application ID (e.g. `application_123456789_0001`) to see container details, allocated memory, vCPUs, and the scheduler queue allocation.
   - Click the **Logs** or **History** links to inspect the standard stdout/stderr logs managed by YARN.

5. Alternatively, list and describe job execution details via `gcloud dataproc jobs` CLI:

```bash
# List Dataproc jobs submitted to the cluster
gcloud dataproc jobs list --region=${REGION}

# Inspect detailed job status and STDOUT/STDERR logs
gcloud dataproc jobs describe [JOB_ID] --region=${REGION}
```

---

## Step 8: Keep Cluster Active for Subsequent Labs

Do **NOT** delete the Dataproc cluster at this stage. Keep the cluster running in state `RUNNING` as it will be reused for subsequent training labs:

```bash
# Verify the cluster remains running for upcoming labs
gcloud dataproc clusters list --region=${REGION}
```
