#!/usr/bin/env python
"""
Lab 2: GCP Pub/Sub Telemetry Publisher
This script reads telemetry data from a CSV file and publishes each record 
directly to a Google Cloud Pub/Sub topic.
"""

import argparse
import csv
import json
import os
import time
from google.cloud import pubsub_v1


def publish_telemetry(project_id, topic_name, csv_file_path):
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return

    # Initialize Pub/Sub Publisher Client
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    print(f"Publishing records from {csv_file_path} to {topic_path}...")

    # Read each record from CSV and publish
    with open(csv_file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            payload_str = json.dumps(row)
            payload_bytes = payload_str.encode("utf-8")
            
            future = publisher.publish(topic_path, data=payload_bytes)
            message_id = future.result()
            print(f"Published message ID: {message_id} | Payload: {payload_str}")
            time.sleep(0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lab 2: Publish CSV rows to Pub/Sub")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--topic", default="lab2-topic", help="Pub/Sub Topic name")
    parser.add_argument("--csv", default="sensor_data.csv", help="Path to CSV file")

    args = parser.parse_args()
    publish_telemetry(args.project, args.topic, args.csv)
