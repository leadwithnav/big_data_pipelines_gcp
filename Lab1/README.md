# Lab 1: Introduction to Apache Spark (PySpark)

In this lab, you will set up a Google Cloud Dataproc cluster, access JupyterLab via the Component Gateway, upload movie dataset files, load them into HDFS, and explore Spark/PySpark fundamentals.

---

## Prerequisites

Before starting, ensure you set your Google Cloud Project ID, enable the required APIs, and grant permissions to the default Compute service account.

### 1. Set Project ID
In your Cloud Shell terminal, set your project identifier:
```bash
export PROJECT_ID=<your project id>
```

### 2. Enable Dataproc API
```bash
gcloud services enable dataproc.googleapis.com \
  --project=232436531464
```

### 3. Enable Resource Manager API
```bash
gcloud services enable cloudresourcemanager.googleapis.com \
  --project=232436531464
```

### 4. Grant Dataproc Worker Role to Compute Default Service Account
Dataproc VMs use the default Compute Engine service account identity to communicate with the cluster manager. Grant it the `Dataproc Worker` role:
```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:232436531464-compute@developer.gserviceaccount.com" \
  --role="roles/dataproc.worker"
```

---

## Step 1: Create the Dataproc Cluster

Run the following command to provision a 2-worker Dataproc cluster with Jupyter support. 

> ⏳ **Note:** This setup will take approximately **5 to 7 minutes** to complete.

```bash
gcloud dataproc clusters create cluster-lab \
  --region=us-central1 \
  --zone=us-central1-b \
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

## Step 2: Download Lab Files

Download the lab files locally to your machine from the following OneDrive Sharepoint directory and extract them:

👉 [Download Lab 1 Files from Sharepoint](https://ueducation-my.sharepoint.com/personal/sujay_maheswarappa_upgrad_com/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fsujay%5Fmaheswarappa%5Fupgrad%5Fcom%2FDocuments%2FExternal%20BigData%20Pipeline%20%2D%208th%20June%2FLabs%2FLab1&viewid=67436d2f%2D7f31%2D4032%2D9f2e%2De6f9cc58bb9c&ga=1)

---

## Step 3: Access JupyterLab and Upload Files

1. In the Google Cloud Console, navigate to **Dataproc → Clusters**.
2. Click on the name of your cluster (**`cluster-lab`**).
3. Open the **Web Interfaces** tab.
4. Click **JupyterLab** (this will open the JupyterLab environment in a new browser tab via Component Gateway).
5. In JupyterLab, click on the **Folder icon** in the left sidebar to navigate the file explorer.
6. Select **Local disk** or navigate to your desired directory.
7. Click the **Upload Files** button (upward arrow icon) in the JupyterLab toolbar and upload the extracted lab files (`movies.csv` and `lab_01_intro.ipynb`).

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
