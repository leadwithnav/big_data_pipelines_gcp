# Lab 1: Introduction to Apache Spark (PySpark)

In this lab, you will set up a Google Cloud Dataproc cluster, access JupyterLab via the Component Gateway, upload movie dataset files, load them into HDFS, and explore Spark/PySpark fundamentals.

---

## Prerequisites

Before starting, ensure you set your Google Cloud Project ID, enable the required APIs, and grant permissions to the default Compute service account.

---

## Step 1: Use Dataproc Cluster created in Lab1

> ⏳ **Note:** If you have not completed Lab1, make sure to run Lab1 to create Dataproc cluster.

---


## Step 3: Access JupyterLab and Upload Files

1. In the Google Cloud Console, navigate to **Dataproc → Clusters**.
2. Click on the name of your cluster (**`cluster-lab`**).
3. Open the **Web Interfaces** tab.
4. Click **JupyterLab** (this will open the JupyterLab environment in a new browser tab via Component Gateway).
5. In JupyterLab, click on the **Folder icon** in the left sidebar to navigate the file explorer.
6. Select **Local disk** or navigate to your desired directory.
7. Click the **Upload Files** button (upward arrow icon) in the JupyterLab toolbar and upload the lab files (`movies.csv` and `lab_01_intro.ipynb`) provided in Lab1 folder.

---

## Step 4: Load `movies.csv` into HDFS

Once the files are uploaded to JupyterLab, copy the dataset into HDFS so that Spark can process it in a distributed filesystem environment.

1. In the JupyterLab Launcher interface, click **Terminal** to open a new terminal session on the master VM node.
2. In the JupyterLab terminal, run the following HDFS CLI commands to create a `/data` folder and load the dataset:
   ```bash
   # Create a directory in HDFS for the movies data
   hdfs dfs -mkdir -p /data
   
   # Load movies.csv from local VM workspace into HDFS
   hdfs dfs -put movies.csv /data/
   
   # Verify the file exists in HDFS
   hdfs dfs -ls /data
   ```

---

## Step 5: Open and Run the PySpark Jupyter Notebook

1. In the JupyterLab file explorer, double-click **`lab_01_intro.ipynb`** to open the interactive notebook.
2. Select the **PySpark** kernel.
3. Verify that the file path in the notebook reads from HDFS (`hdfs:///data/movies.csv` or `/data/movies.csv`).
4. Execute the cells sequentially to run Spark transformations and actions.
