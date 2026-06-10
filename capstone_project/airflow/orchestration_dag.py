"""
Airflow Orchestration DAG for Walmart GCP Retail Pipeline.
Deploys daily Spark ETL job on Dataproc, triggers BigQuery sync, 
runs data quality checks, and executes Iceberg snapshot compaction maintenance.
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
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

# ---------------------------------------------------------------------------
# Default Configurations
# ---------------------------------------------------------------------------

try:
    _, google_project = google.auth.default()
except Exception:
    google_project = None

PROJECT_ID = google_project or os.environ.get("GCP_PROJECT") or "YOUR_GCP_PROJECT_ID"
REGION = "us-central1"
CLUSTER_NAME = "walmart-retail-etl-cluster"
RAW_WAREHOUSE = f"gs://{PROJECT_ID}-iceberg-raw/warehouse"
CURATED_WAREHOUSE = f"gs://{PROJECT_ID}-iceberg-curated/warehouse"
SPARK_ETL_SCRIPT = f"gs://{PROJECT_ID}-code-bin/dataproc/spark_etl_job.py"

default_args = {
    "owner": "retail-data-platform",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["alerts-retail@walmart.com"],
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ---------------------------------------------------------------------------
# Cluster Configuration
# ---------------------------------------------------------------------------

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
            "spark:spark.jars": f"gs://{PROJECT_ID}-code-bin/libs/iceberg-spark-runtime-3.5_2.12-1.5.2.jar",
        },
    },
}

# ---------------------------------------------------------------------------
# Job Configuration
# ---------------------------------------------------------------------------

PYSPARK_JOB = {
    "reference": {"project_id": PROJECT_ID},
    "placement": {"cluster_name": CLUSTER_NAME},
    "pyspark_job": {
        "main_python_file_uri": SPARK_ETL_SCRIPT,
        "args": [
            "--raw_warehouse", RAW_WAREHOUSE,
            "--curated_warehouse", CURATED_WAREHOUSE,
        ],
    },
}

# ---------------------------------------------------------------------------
# DAG Definition
# ---------------------------------------------------------------------------

with DAG(
    "walmart_retail_pipeline_orchestration",
    default_args=default_args,
    description="Daily retail ingestion & curated analytics pipeline orchestration",
    schedule_interval="@daily",
    start_date=datetime(2026, 6, 10),
    catchup=False,
    max_active_runs=1,
) as dag:

    start_pipeline = EmptyOperator(task_id="start_pipeline")

    # 1. Spin up ephemeral Dataproc Cluster with Iceberg support
    create_dataproc_cluster = DataprocCreateClusterOperator(
        task_id="create_dataproc_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        cluster_config=CLUSTER_CONFIG,
        region=REGION,
    )

    # 2. Run PySpark Batch Aggregations and MERGE INTO logic
    run_spark_etl = DataprocSubmitJobOperator(
        task_id="run_spark_etl",
        job=PYSPARK_JOB,
        region=REGION,
        project_id=PROJECT_ID,
    )

    # 3. Clean up cluster to save costs
    delete_dataproc_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        region=REGION,
        trigger_rule="all_done",
    )

    # 4. BigQuery External Table Sync / View Refreshes
    refresh_bigquery_reports = BigQueryExecuteQueryOperator(
        task_id="refresh_bigquery_reports",
        sql=f"""
            -- Materialize reporting aggregate metrics in BigQuery
            CREATE OR REPLACE TABLE `{PROJECT_ID}.retail_analytics.daily_store_revenue` AS
            SELECT 
                date,
                store_id,
                sum(total_revenue) as daily_revenue,
                sum(total_quantity) as units_sold
            FROM `{PROJECT_ID}.retail_analytics.sales_daily_external`
            GROUP BY 1, 2;
        """,
        use_legacy_sql=False,
        write_disposition="WRITE_TRUNCATE",
    )

    # 5. Data Quality Checks Task (Example checks)
    run_data_quality_checks = BigQueryExecuteQueryOperator(
        task_id="run_data_quality_checks",
        sql=f"""
            -- Check that daily store revenue is never negative
            ASSERT (SELECT count(*) FROM `{PROJECT_ID}.retail_analytics.daily_store_revenue` WHERE daily_revenue < 0) = 0
            AS 'Data Quality Error: Detected negative daily store revenue!';
        """,
        use_legacy_sql=False,
    )

    # 6. Iceberg Table Maintenance (Snapshot Expiration & File Compaction)
    # This runs as a PySpark submit or using Dataproc Serverless / Spark SQL
    run_iceberg_maintenance = DataprocSubmitJobOperator(
        task_id="run_iceberg_maintenance",
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "spark_sql_job": {
                "query_list": {
                    "queries": [
                        # Expire old snapshots older than 7 days
                        "CALL curated_cat.system.expire_snapshots('curated_data.sales_daily', TIMESTAMP 'now() - INTERVAL 7 DAYS');",
                        "CALL curated_cat.system.expire_snapshots('curated_data.inventory_by_store', TIMESTAMP 'now() - INTERVAL 7 DAYS');",
                        # Rewrite manifest files to optimize query plans (compaction)
                        "CALL curated_cat.system.rewrite_manifests('curated_data.sales_daily');",
                        "CALL curated_cat.system.rewrite_manifests('curated_data.inventory_by_store');"
                    ]
                }
            }
        },
        region=REGION,
        project_id=PROJECT_ID,
    )

    end_pipeline = EmptyOperator(task_id="end_pipeline")

    # Workflow dependencies
    start_pipeline >> create_dataproc_cluster >> run_spark_etl >> run_iceberg_maintenance >> delete_dataproc_cluster
    delete_dataproc_cluster >> refresh_bigquery_reports >> run_data_quality_checks >> end_pipeline
