#!/usr/bin/env python
"""
Lab 2: GCP Pub/Sub Telemetry Publisher
This script reads telemetry data from a CSV file and publishes the records 
indefinitely to a Google Cloud Pub/Sub topic, injecting the current UTC timestamp
into each payload.
"""

import argparse
import csv
import itertools
import json
import logging
import os
import time
from datetime import datetime, timezone
from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists


def publish_telemetry(project_id, topic_name, csv_file_path, interval):
    """Loads records from CSV and publishes them indefinitely to Pub/Sub."""
    if not os.path.exists(csv_file_path):
        logging.error(f"CSV file not found at: {csv_file_path}")
        return

    # Load all records from the CSV file into memory
    logging.info(f"Loading records from {csv_file_path}...")
    records = []
    
    with open(csv_file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Format fields appropriately
                record = {
                    "device_id": row["device_id"],
                    "temperature": float(row["temperature"]),
                    "humidity": float(row["humidity"]),
                    "status": row["status"]
                }
                records.append(record)
            except KeyError as e:
                logging.error(f"Missing expected column in CSV: {e}")
                return
            except ValueError as e:
                logging.warning(f"Failed to parse row {row}: {e}. Skipping.")

    if not records:
        logging.error("No valid records found in the CSV file.")
        return

    logging.info(f"Successfully loaded {len(records)} records.")

    # Initialize the Pub/Sub Publisher Client
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    # Attempt to create the topic. If it already exists, just proceed.
    try:
        publisher.create_topic(request={"name": topic_path})
        logging.info(f"Created Pub/Sub topic: {topic_path}")
    except AlreadyExists:
        logging.info(f"Pub/Sub topic already exists: {topic_path}")
    except Exception as e:
        logging.warning(
            f"Could not check/create topic {topic_path} directly. "
            f"Will attempt to publish assuming it exists. Error: {e}"
        )

    logging.info(
        f"Starting data publisher. Publishing to {topic_path} every {interval}s. "
        "Press Ctrl+C to stop."
    )

    try:
        # Loop over the records indefinitely
        for record in itertools.cycle(records):
            # Create a copy to avoid mutating the source in-memory data
            payload = record.copy()
            # Inject the latest UTC timestamp
            payload["timestamp"] = datetime.now(timezone.utc).isoformat()

            # Convert reading payload to JSON bytes
            payload_str = json.dumps(payload)
            payload_bytes = payload_str.encode("utf-8")

            # Publish the message
            future = publisher.publish(
                topic_path,
                data=payload_bytes,
                device_id=payload["device_id"],
                timestamp=payload["timestamp"]
            )

            # Wait for publication result to verify it succeeded
            message_id = future.result()
            logging.info(f"Published message ID: {message_id} | Payload: {payload_str}")

            time.sleep(interval)

    except KeyboardInterrupt:
        logging.info("Publisher stopped by user.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    parser = argparse.ArgumentParser(description="Lab 2: Publish IoT Pub/Sub Telemetry from CSV")
    parser.add_argument(
        "--project",
        required=True,
        help="GCP Project ID"
    )
    parser.add_argument(
        "--topic",
        default="lab2-topic",
        help="Pub/Sub Topic name (default: lab2-topic)"
    )
    parser.add_argument(
        "--csv",
        default="sensor_data.csv",
        help="Path to the source CSV file (default: sensor_data.csv)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Interval between messages in seconds (default: 0.5)"
    )

    args = parser.parse_args()
    publish_telemetry(args.project, args.topic, args.csv, args.interval)
