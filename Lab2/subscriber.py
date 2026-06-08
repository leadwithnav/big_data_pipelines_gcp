#!/usr/bin/env python
"""
Lab 2: GCP Pub/Sub Telemetry Subscriber
This script subscribes to a Google Cloud Pub/Sub subscription,
receives messages asynchronously, and acknowledges them.
"""

import argparse
from google.cloud import pubsub_v1


def callback(message):
    payload_str = message.data.decode("utf-8")
    print(f"Received message ID: {message.message_id} | Payload: {payload_str}")
    message.ack()


def subscribe_telemetry(project_id, subscription_name):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)

    print(f"Listening for messages on {subscription_path}... Press Ctrl+C to stop.")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
        print("Subscriber stopped by user.")
    except Exception as e:
        print(f"Subscriber exited with error: {e}")
        streaming_pull_future.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lab 2: Subscribe and print Pub/Sub messages")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--subscription", default="lab2-sub", help="Pub/Sub Subscription name")

    args = parser.parse_args()
    subscribe_telemetry(args.project, args.subscription)
