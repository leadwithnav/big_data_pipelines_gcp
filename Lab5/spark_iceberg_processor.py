#!/usr/bin/env python
"""
Lab 5: PySpark Iceberg Data Processor

This Spark program:
1. Configures a SparkSession with Apache Iceberg extensions.
2. Defines two Hadoop Catalogs:
   - `input_cat`: points to the staging GCS bucket warehouse (written by Apache Beam).
   - `output_cat`: points to the new destination GCS bucket warehouse for processed aggregates.
3. Reads the Iceberg table `sensor_db.aggregates` from `input_cat`.
4. Filters the data to find alerts (high temperatures or sensor errors).
5. Writes the filtered output in Iceberg format to `output_cat.sensor_db.processed_alerts`.

Can be executed on a Dataproc Cluster or using spark-submit:
    spark-submit \
        --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2 \
        spark_iceberg_processor.py \
        --input_warehouse gs://YOUR_STAGING_BUCKET/warehouse \
        --output_warehouse gs://YOUR_OUTPUT_BUCKET/processed_warehouse
"""

import argparse
import logging
from pyspark.sql import SparkSession


def process_telemetry(input_warehouse, output_warehouse):
    # Initialize the Spark Session with Iceberg configurations
    logging.info("Initializing Spark Session with Iceberg support...")
    spark = SparkSession.builder \
        .appName("Lab5-Spark-Iceberg-Processor") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.input_cat", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.input_cat.type", "hadoop") \
        .config("spark.sql.catalog.input_cat.warehouse", input_warehouse) \
        .config("spark.sql.catalog.output_cat", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.output_cat.type", "hadoop") \
        .config("spark.sql.catalog.output_cat.warehouse", output_warehouse) \
        .getOrCreate()

    try:
        # 1. Read the Iceberg table created by the Beam streaming pipeline
        input_table = "input_cat.sensor_db.aggregates"
        logging.info(f"Reading from input Iceberg table: {input_table} ...")
        aggregates_df = spark.read.table(input_table)

        # Print Schema and Sample Records for verification
        logging.info("Schema of input table:")
        aggregates_df.printSchema()
        logging.info("Displaying sample input records:")
        aggregates_df.show(truncate=False)

        # 2. Process the data (Filter to identify alerts/errors)
        # Find windows where average temperature > 25.0 OR error count > 0
        logging.info("Filtering records to find anomalous sensor alerts...")
        alerts_df = aggregates_df.filter(
            (aggregates_df.avg_temperature > 25.0) | (aggregates_df.error_count > 0)
        )

        logging.info("Anomalous sensor alerts identified:")
        alerts_df.show(truncate=False)

        # 3. Write the results back in Iceberg format to the new GCS bucket warehouse
        output_table = "output_cat.sensor_db.processed_alerts"
        logging.info(f"Writing alerts to output Iceberg table: {output_table} ...")
        
        # Write mode 'append' will add new records; will create table if it does not exist
        alerts_df.write \
            .format("iceberg") \
            .mode("append") \
            .saveAsTable(output_table)

        logging.info("Successfully wrote processed alerts in Iceberg format to destination GCS bucket.")

    except Exception as e:
        logging.error(f"Error during Spark processing: {e}", exc_info=True)
    finally:
        spark.stop()
        logging.info("Spark Session stopped.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    parser = argparse.ArgumentParser(description="PySpark Job to process GCS Iceberg tables")
    parser.add_argument(
        "--input_warehouse",
        required=True,
        help="GCS base path of the input Iceberg warehouse (e.g. gs://STAGE_BUCKET/warehouse)"
    )
    parser.add_argument(
        "--output_warehouse",
        required=True,
        help="GCS base path of the destination Iceberg warehouse (e.g. gs://OUTPUT_BUCKET/processed_warehouse)"
    )

    args = parser.parse_args()
    process_telemetry(args.input_warehouse, args.output_warehouse)
