"""
PySpark Iceberg ETL Job for Lab 7.
Reads telemetry from gcs_hadoop_catalog.sensor_db.filtered_readings,
aggregates metrics (avg temp, avg humidity) by device and day,
and writes the results back to gcs_hadoop_catalog.sensor_db.aggregated_readings.
"""

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, substring, avg, count

def main():
    parser = argparse.ArgumentParser(description="Dataproc Batch PySpark Iceberg ETL")
    parser.add_argument("--warehouse_path", required=True, help="GCS Iceberg warehouse GCS path (e.g. gs://[BUCKET]/warehouse)")
    args = parser.parse_known_args()[0]

    # Initialize Spark Session with GCS Iceberg Catalog
    spark = SparkSession.builder \
        .appName("Lab7-Spark-Iceberg-ETL") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.gcs_hadoop_catalog", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.gcs_hadoop_catalog.catalog-impl", "org.apache.iceberg.hadoop.HadoopCatalog") \
        .config("spark.sql.catalog.gcs_hadoop_catalog.warehouse", args.warehouse_path) \
        .getOrCreate()

    # Define table paths
    source_table = "gcs_hadoop_catalog.sensor_db.filtered_readings"
    target_table = "gcs_hadoop_catalog.sensor_db.aggregated_readings"

    print(f"Reading telemetry data from Iceberg table: {source_table}")
    # Load source Iceberg table
    df_raw = spark.read.table(source_table)
    
    print("Executing aggregation transformations...")
    # Perform aggregation: average temperature/humidity and total counts by device and date
    df_agg = df_raw.withColumn("date", substring(col("timestamp"), 1, 10)) \
        .groupBy("device_id", "date") \
        .agg(
            avg("temperature").alias("avg_temperature"),
            avg("humidity").alias("avg_humidity"),
            count("device_id").alias("reading_count")
        )

    print(f"Creating and loading target Iceberg table: {target_table}")
    # Create target database if it doesn't exist
    spark.sql("CREATE DATABASE IF NOT EXISTS gcs_hadoop_catalog.sensor_db")
    
    # Save transformed data back to GCS as an Iceberg table
    df_agg.write \
        .format("iceberg") \
        .mode("overwrite") \
        .save(target_table)

    print("ETL Job completed successfully. Displaying top 10 aggregated records:")
    spark.read.table(target_table).show(10, truncate=False)

    spark.stop()

if __name__ == "__main__":
    main()
