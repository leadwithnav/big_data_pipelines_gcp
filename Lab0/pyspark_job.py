#!/usr/bin/env python
"""
Lab 0: PySpark Telemetry Aggregator

This job is designed to run on a Google Cloud Dataproc cluster managed by YARN:
1. Initializes a SparkSession.
2. Reads sensor readings from HDFS (default: hdfs:///user/telemetry/sensor_data.csv).
3. Groups the readings by `device_id` and calculates record counts, average temperature, and average humidity.
4. Outputs the aggregates to stdout (viewable in YARN Resource Manager).
5. Writes the aggregated output back to HDFS in CSV format.
"""

import argparse
import logging
from pyspark.sql import SparkSession
import pyspark.sql.functions as F


def main(input_path, output_path):
    # Initialize Spark Session
    # Dataproc pre-configures Spark to submit jobs to the YARN scheduler automatically
    spark = SparkSession.builder \
        .appName("Lab0-HDFS-Telemetry-Aggregator") \
        .getOrCreate()

    logging.info(f"Connected to Spark. Reading input from HDFS: {input_path}")

    try:
        # 1. Read CSV from HDFS
        df = spark.read.csv(input_path, header=True, inferSchema=True)

        logging.info("Input Dataset Schema:")
        df.printSchema()

        logging.info("First 5 records from HDFS:")
        df.show(5)

        # 2. Perform Aggregation
        logging.info("Running aggregations (count and averages)...")
        aggregated_df = df.groupBy("device_id").agg(
            F.count("device_id").alias("record_count"),
            F.round(F.avg("temperature"), 2).alias("avg_temperature"),
            F.round(F.avg("humidity"), 2).alias("avg_humidity")
        ).orderBy("device_id")

        # 3. Print results to console (YARN logs)
        logging.info("Aggregated metrics per device ID:")
        aggregated_df.show()

        # 4. Write results back to HDFS
        if output_path:
            logging.info(f"Writing aggregated results to HDFS: {output_path}")
            aggregated_df.write \
                .mode("overwrite") \
                .option("header", "true") \
                .csv(output_path)
            logging.info("Write complete.")

    except Exception as e:
        logging.error(f"Error executing Spark Job: {e}", exc_info=True)
    finally:
        spark.stop()
        logging.info("Spark Session stopped.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    parser = argparse.ArgumentParser(description="Lab 0 PySpark Job")
    parser.add_argument(
        "--input",
        default="hdfs:///user/telemetry/sensor_data.csv",
        help="Input CSV path in HDFS (default: hdfs:///user/telemetry/sensor_data.csv)"
    )
    parser.add_argument(
        "--output",
        default="hdfs:///user/telemetry/output",
        help="Output CSV path in HDFS (default: hdfs:///user/telemetry/output)"
    )

    args = parser.parse_args()
    main(args.input, args.output)
