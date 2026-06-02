# Lab 1: Introduction to Apache Spark (PySpark)

Welcome to the first lab! This lab demonstrates the fundamental concepts of Apache Spark using PySpark, Spark's Python API. We will use a small dataset of movies to explore basic operations.

## Learning Objectives

In this lab, you will learn how to:
- Initialize a `SparkSession`.
- Read a CSV dataset into a Spark DataFrame.
- Explore data structure and schema.
- Perform basic transformations (like `filter` and `select`).
- Perform complex transformations using functions (like `split`, `explode`, `groupBy`).
- Execute actions (like `show`, `count`) and write data back to storage.

## Files Included

- **`movies.csv`**: A sample dataset containing basic movie information (`movieId`, `title`, `genres`, `year`, `rating`).
- **`lab_01_intro.py`**: A standard PySpark Python script containing the lab code.
- **`lab_01_intro.ipynb`**: A Jupyter Notebook containing the same lab code, split into interactive cells.

## Running on Google Cloud Dataproc

This lab is designed to be fully compatible with GCP Dataproc.

### Option A: Using the Python Script (`lab_01_intro.py`)

If you want to submit the job to a Dataproc cluster, you can use the `gcloud` command-line tool.
(Note: You should upload `movies.csv` to Google Cloud Storage (GCS) and update the `file_path` in the script to your `gs://...` path for a real cluster environment).

To run locally or on the master node of your cluster:
```bash
spark-submit lab_01_intro.py
```

To submit to a Dataproc cluster:
```bash
gcloud dataproc jobs submit pyspark lab_01_intro.py \
    --cluster=YOUR_CLUSTER_NAME \
    --region=YOUR_REGION
```

### Option B: Using the Jupyter Notebook (`lab_01_intro.ipynb`)

Dataproc supports the Jupyter component. If your cluster was created with Jupyter enabled, you can upload `lab_01_intro.ipynb` directly to the Jupyter UI in Dataproc.

1. Navigate to your Dataproc Cluster in the Google Cloud Console.
2. Under "Web Interfaces", click on "Jupyter".
3. Upload `lab_01_intro.ipynb` and `movies.csv` to your Jupyter workspace.
4. Open the notebook and run the cells sequentially.

## Expected Output

You will see Spark log messages followed by the outputs of our actions, including:
- The schema of the `movies` dataset.
- A list of movies released after 2000.
- Top-rated movies.
- The average rating per individual genre.
- A success message indicating data was written to the `output/genre_ratings` folder.
