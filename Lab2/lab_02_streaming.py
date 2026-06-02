#!/usr/bin/env python
# coding: utf-8

"""
Lab 2: Spark Structured Streaming with Pub/Sub (Avro)

This PySpark script reads real-time Avro data from a Pub/Sub topic,
processes the orders, and writes the results back to another Pub/Sub topic as JSON.
"""

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_json, struct
from pyspark.sql.avro.functions import from_avro

def main():
    if len(sys.argv) != 4:
        print("Usage: spark-submit lab_02_streaming.py <project_id> <input_topic> <output_topic>")
        sys.exit(1)

    project_id = sys.argv[1]
    input_topic = sys.argv[2]
    output_topic = sys.argv[3]

    print("="*50)
    print("Starting Lab 2: Spark Structured Streaming (Avro)")
    print(f"Project ID: {project_id}")
    print(f"Input Topic: {input_topic}")
    print(f"Output Topic: {output_topic}")
    print("="*50)

    # 1. Initialize SparkSession
    spark = SparkSession.builder \
        .appName("Lab 2 - Pub/Sub Streaming (Avro)") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 2. Define the Avro schema string
    avro_schema = """
    {
      "type": "record",
      "name": "Avro",
      "fields": [
        {"name": "orderId", "type": "string"},
        {"name": "amount", "type": "float"},
        {"name": "quantiy", "type": "int"}
      ]
    }
    """

    # 3. Read Stream from Pub/Sub
    print(f"Subscribing to {input_topic}...")
    try:
        raw_stream_df = spark.readStream \
            .format("pubsub") \
            .option("project", project_id) \
            .option("topic", input_topic) \
            .load()
    except Exception as e:
        print("Warning: Could not start read stream using format 'pubsub'. Are you running on Dataproc?")
        raise e

    # 4. Parse Avro Data
    # The Pub/Sub payload is available in the 'value' column as bytes.
    # We use from_avro to deserialize the bytes into a struct based on the schema.
    parsed_df = raw_stream_df \
        .select(from_avro(col("value"), avro_schema).alias("data")) \
        .select("data.*")

    # 5. Process Data: Calculate total value for the order
    processed_df = parsed_df.withColumn("total_value", col("amount") * col("quantiy"))

    # 6. Format for Output
    # Convert the processed columns into a JSON string to write back to Pub/Sub
    output_df = processed_df.select(
        to_json(struct(
            col("orderId"), 
            col("amount"), 
            col("quantiy"), 
            col("total_value")
        )).alias("value")
    )
    
    # Cast to binary for the pubsub connector
    output_df = output_df.withColumn("value", col("value").cast("binary"))

    # 7. Write Stream to Pub/Sub
    print(f"Writing to {output_topic}...")
    output_df.writeStream \
        .format("console") \
        .outputMode("append") \
        .start()

    print("Streaming query started! Waiting for termination...")
    query.awaitTermination()

if __name__ == "__main__":
    main()
