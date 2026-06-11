"""
Simple test Airflow DAG for Lab 8.
Runs Python and Bash tasks to verify that the Composer environment is functioning correctly.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow-test",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

def run_test():
    print("Airflow Python environment test successful! Task run complete.")

with DAG(
    "lab8_simple_test_dag",
    default_args=default_args,
    description="A simple DAG to test Cloud Composer environment execution",
    schedule_interval=None,
    start_date=datetime(2026, 6, 10),
    catchup=False,
    max_active_runs=1,
) as dag:

    # 1. Bash task
    bash_task = BashOperator(
        task_id="bash_test_task",
        bash_command="echo 'Hello from Apache Airflow on Cloud Composer!'",
    )

    # 2. Python task
    python_task = PythonOperator(
        task_id="python_test_task",
        python_callable=run_test,
    )

    bash_task >> python_task
