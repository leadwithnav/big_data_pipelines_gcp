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
    parser.add_argument("--input_csv_path", required=False, help="GCS path of the input sensor.csv file (e.g. gs://[BUCKET]/sensor.csv)")
    args = parser.parse_known_args()[0]

    # Resolve input GCS CSV path
    input_csv_path = args.input_csv_path
    if not input_csv_path:
        if args.warehouse_path.startswith("gs://"):
            bucket = args.warehouse_path[5:].split("/")[0]
            input_csv_path = f"gs://{bucket}/sensor.csv"
        else:
            input_csv_path = "sensor.csv"

    # Initialize Spark Session with GCS Iceberg Catalog (HadoopCatalog)
    spark = SparkSession.builder \
        .appName("Lab8-Spark-Iceberg-ETL") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.gcs_hadoop_catalog", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.gcs_hadoop_catalog.catalog-impl", "org.apache.iceberg.hadoop.HadoopCatalog") \
        .config("spark.sql.catalog.gcs_hadoop_catalog.warehouse", args.warehouse_path) \
        .getOrCreate()

    print(f"Reading raw telemetry data from CSV: {input_csv_path}")
    # Load source CSV file from GCS
    df_raw = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(input_csv_path)
    
    print("Executing aggregation transformations...")
    # Perform aggregation: average temperature grouped by device_id
    df_agg = df_raw.groupBy("device_id") \
        .agg(avg("temperature").alias("temperature"))

    print("Mapping columns to match dataset3.iceberg_tbl1 schema (id, sensor_id, temperature)...")
    # Add an ID column (row number + offset) and rename device_id to sensor_id
    windowSpec = Window.orderBy("device_id")
    df_final = df_agg.withColumn("id", row_number().over(windowSpec) + lit(1005)) \
        .withColumnRenamed("device_id", "sensor_id") \
        .withColumn("sensor_id", col("sensor_id").cast("string")) \
        .select("id", "sensor_id", "temperature")

    output_path = args.warehouse_path.rstrip("/") + "/aggregated_readings"
    print(f"Writing aggregated data directly to GCS in Iceberg format: {output_path}")
    # Save the results directly to GCS in Iceberg format
    df_final.write \
        .format("iceberg") \
        .mode("overwrite") \
        .save(output_path)

    print("ETL Job completed successfully. Displaying appended records:")
    df_final.show(10, truncate=False)

    spark.stop()

if __name__ == "__main__":
    main()
