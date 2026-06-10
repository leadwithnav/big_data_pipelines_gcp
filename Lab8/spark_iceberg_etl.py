"""
PySpark Iceberg ETL Job for Lab 8.
Reads telemetry from gcs_hadoop_catalog.sensor_db.filtered_readings,
aggregates average temperature by device, and appends the result
directly to the existing GCS path of the BigQuery Managed Iceberg table.
"""

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, row_number, lit
from pyspark.sql.window import Window

def main():
    parser = argparse.ArgumentParser(description="Dataproc Batch PySpark Iceberg ETL")
    parser.add_argument("--warehouse_path", required=True, help="GCS path of the target Managed Iceberg table (e.g. gs://[BUCKET]/warehouse)")
    args = parser.parse_known_args()[0]

    # Initialize Spark Session with GCS Iceberg Catalog (HadoopCatalog)
    spark = SparkSession.builder \
        .appName("Lab8-Spark-Iceberg-ETL") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.gcs_hadoop_catalog", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.gcs_hadoop_catalog.catalog-impl", "org.apache.iceberg.hadoop.HadoopCatalog") \
        .config("spark.sql.catalog.gcs_hadoop_catalog.warehouse", args.warehouse_path) \
        .getOrCreate()

    source_table = "gcs_hadoop_catalog.sensor_db.filtered_readings"
    
    print(f"Reading raw telemetry data from Iceberg table: {source_table}")
    # Load source Iceberg table
    df_raw = spark.read.table(source_table)
    
    print("Executing aggregation transformations...")
    # Perform aggregation: average temperature grouped by device_id
    df_agg = df_raw.groupBy("device_id") \
        .agg(avg("temperature").alias("temperature"))

    print("Mapping columns to match dataset3.iceberg_tbl1 schema (id, sensor_id, temperature)...")
    # Add an ID column (row number + offset) and rename device_id to sensor_id
    windowSpec = Window.orderBy("device_id")
    df_final = df_agg.withColumn("id", row_number().over(windowSpec) + lit(1005)) \
        .withColumnRenamed("device_id", "sensor_id") \
        .select("id", "sensor_id", "temperature")

    print(f"Appending aggregated data directly to existing GCS Managed Iceberg path: {args.warehouse_path}")
    # Append the results directly to the existing GCS Iceberg table storage path
    df_final.write \
        .format("iceberg") \
        .mode("append") \
        .save(args.warehouse_path)

    print("ETL Job completed successfully. Displaying appended records:")
    df_final.show(10, truncate=False)

    spark.stop()

if __name__ == "__main__":
    main()
