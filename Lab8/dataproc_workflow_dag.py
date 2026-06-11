"""
Airflow Orchestration DAG for Lab 8.
Manages the lifecycle of an ephemeral Dataproc cluster:
1. Spin up Dataproc cluster pre-configured with Iceberg Spark jar.
2. Submit the PySpark ETL batch job for Lab 8 (writing to existing BigQuery Managed Iceberg).
3. Tear down cluster to save costs (failsafe trigger rule).
"""

import os
import google.auth
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocDeleteClusterOperator,
    DataprocSubmitJobOperator,
)

# ---------------------------------------------------------------------------
# Dynamic Config Resolutions
# ---------------------------------------------------------------------------

try:
    _, google_project = google.auth.default()
except Exception:
    google_project = None

PROJECT_ID = google_project or os.environ.get("GCP_PROJECT") or "YOUR_GCP_PROJECT_ID"
REGION = "us-central1"
ZONE = "us-central1-a"
CLUSTER_NAME = "lab8-ephemeral-dataproc-cluster"

# Warehouse path pointing directly to the GCS folder of the BigQuery Managed Iceberg table
WAREHOUSE_PATH = f"gs://{PROJECT_ID}-iceberg-warehouse/warehouse"
INPUT_CSV_PATH = f"gs://{PROJECT_ID}-iceberg-warehouse/sensor.csv"
SPARK_ETL_SCRIPT = f"gs://{PROJECT_ID}-code-bin/dataproc/spark_iceberg_etl_lab8.py"
ICEBERG_JAR_URI = f"gs://{PROJECT_ID}-code-bin/libs/iceberg-spark-runtime-3.5_2.12-1.5.2.jar"

# ---------------------------------------------------------------------------
# Dag Configurations
# ---------------------------------------------------------------------------

default_args = {
    "owner": "airflow-telemetry-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

# Cluster configuration with Iceberg extension and GCS jar pre-configured
CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n2-standard-4",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 100},
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n2-standard-2",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 100},
    },
    "software_config": {
        "image_version": "2.2-debian12",
        "properties": {
            "spark:spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            "spark:spark.jars": ICEBERG_JAR_URI,
        },
    },
    "gce_cluster_config": {
        "zone_uri": ZONE,
        "internal_ip_only": False,
    }
}

PYSPARK_JOB = {
    "reference": {"project_id": PROJECT_ID},
    "placement": {"cluster_name": CLUSTER_NAME},
    "pyspark_job": {
        "main_python_file_uri": SPARK_ETL_SCRIPT,
        "args": [
            "--warehouse_path", WAREHOUSE_PATH,
            "--input_csv_path", INPUT_CSV_PATH
        ],
    },
}

# ---------------------------------------------------------------------------
# DAG Definition
# ---------------------------------------------------------------------------

with DAG(
    "lab8_dataproc_lifecycle_orchestration",
    default_args=default_args,
    description="Orchestrates Dataproc lifecycle and runs Spark Iceberg ETL for Lab 8",
    schedule_interval=None,
    start_date=datetime(2026, 6, 10),
    catchup=False,
    max_active_runs=1,
) as dag:

    # 1. Spin up ephemeral Dataproc cluster
    create_dataproc_cluster = DataprocCreateClusterOperator(
        task_id="create_dataproc_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        cluster_config=CLUSTER_CONFIG,
        region=REGION,
    )

    # 2. Submit the PySpark Iceberg ETL script
    run_spark_iceberg_etl = DataprocSubmitJobOperator(
        task_id="run_spark_iceberg_etl",
        job=PYSPARK_JOB,
        region=REGION,
        project_id=PROJECT_ID,
    )

    # 3. Clean up the cluster (trigger_rule="all_done" to run even if Spark task fails)
    delete_dataproc_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        region=REGION,
        trigger_rule="all_done",
    )

    # Define Workflow Sequence
    create_dataproc_cluster >> run_spark_iceberg_etl >> delete_dataproc_cluster
