# Lab 1.1: Spark Architecture - Partitions, Jobs, Stages, and Tasks

In this lab, you will explore Spark's core execution model. You will load a MovieLens-style dataset `ratings.csv` from HDFS and run PySpark operations to understand how Spark manages **Partitions** in memory, splits operations into **Jobs**, divides them into **Stages** based on shuffles, and executes them as concurrent **Tasks**.

You will also use the **Spark Application UI / Spark History Server** to inspect the DAG (Directed Acyclic Graph) and visualize how your code translates to execution units.

```
+─────────────────────────────────────────────────────────────────────────────+
|                          Google Cloud Dataproc                              |
|                                                                             |
|   +───────────────────────────────+      Spark Application UI               |
|   |         HDFS Storage          |      - Visualizes DAG Execution         |
|   |      /data/ratings.csv        |      - Shows Job -> Stage -> Task Split |
|   +───────────────────────────────+      - Tracks shuffles & memory usage   |
|                   ▲                                                         |
|                   │ (Reads & Analyzes)                                      |
|   +───────────────────────────────+                                         |
|   |    spark_architecture.ipynb   |                                         |
|   |  (Partitions/Narrow/Wide Demos)|                                        |
|   +───────────────────────────────+                                         |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## Prerequisites

- A Google Cloud project with billing enabled.
- Dataproc APIs enabled.
- Access to Cloud Shell.
- An active Dataproc Cluster. *(You can reuse the **`cluster-lab`** cluster created in **Lab 1**! If your cluster is running, skip to Step 2).*

---

## Step 1: Create the Dataproc Cluster (If not already running)

If you do not have an active cluster, launch one in Cloud Shell:

```bash
export PROJECT_ID=<your project id>
export REGION=us-central1

gcloud dataproc clusters create cluster-lab \
  --region=${REGION} \
  --zone=${REGION}-b \
  --num-workers=2 \
  --master-machine-type=n2-standard-4  \
  --worker-machine-type=n2-standard-4  \
  --master-boot-disk-size=30GB \
  --worker-boot-disk-size=30GB \
  --enable-component-gateway \
  --optional-components=JUPYTER \
  --project=${PROJECT_ID}
```

---

## Step 2: Access JupyterLab and Upload Files

1. Navigate to **Dataproc → Clusters** in the Google Cloud Console.
2. Click your cluster name (`cluster-lab`).
3. Click the **Web Interfaces** tab and open **JupyterLab**.
4. In the JupyterLab left sidebar, click the **Folder icon**.
5. Upload the local lab files from your machine:
   - **`ratings.csv`** (the ratings dataset)
   - **`spark_architecture.ipynb`** (the PySpark execution notebook)

---

## Step 3: Load `ratings.csv` into HDFS

To analyze partitions and stages on a distributed filesystem, we will copy the local CSV dataset into HDFS.

1. In JupyterLab, open a **Terminal** from the Launcher menu.
2. Run the following HDFS CLI commands to create the directory and upload the file:
   ```bash
   # Create a directory in HDFS (skip if /data was created in Lab 1)
   hdfs dfs -mkdir -p /data
   
   # Load ratings.csv from local workspace into HDFS
   hdfs dfs -put ratings.csv /data/
   
   # Verify the file is stored in HDFS
   hdfs dfs -ls /data
   ```

---

## Step 4: Open and Run the Jupyter Notebook

1. In JupyterLab, double-click **`spark_architecture.ipynb`**.
2. Set the kernel to **PySpark**.
3. Run the cells sequentially to perform Spark transformations (filter, groupBy) and actions (count, show).

---

## Step 5: Explore Jobs, Stages, and Tasks in Spark UI

Observe how your notebook operations translate to the Spark Application UI:

1. Return to the Google Cloud Console in the **Web Interfaces** tab for your cluster.
2. Click **Spark History Server** or **Spark Application UI**.
3. Locate your active or completed session `Lab1_1-Spark-Architecture-Exploration` under the application list.
4. Navigate through the tabs:
   - **Jobs Tab:** Notice that every action called in the notebook (such as `.count()` or `.show()`) initiated a separate Spark **Job**.
   - **Stages Tab:** Check your Jobs detail:
     - The **Filter** operation (narrow transformation) ran in **1 Stage** because data did not need to be shuffled.
     - The **GroupBy** aggregation (wide transformation) ran in **2 Stages** due to the shuffle boundary required to group ratings by movie ID.
     - Under the DAG visualization, observe the shuffle stages.
   - **Tasks Detail:** Click on a Stage. Note the number of **Tasks** launched matches the number of partitions. For instance, if a Stage has 4 partitions, Spark launched exactly 4 Tasks in parallel.

---

## Step 6: Cleanup

Delete your cluster when finished to avoid GCE worker instances charging your account:

```bash
gcloud dataproc clusters delete cluster-lab --region=us-central1 --quiet
```
