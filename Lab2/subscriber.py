#!/usr/bin/env python
"""
Lab 2: GCP Pub/Sub Telemetry Subscriber
This script subscribes to a Google Cloud Pub/Sub subscription,
receives messages asynchronously, logs their content in real-time,
and acknowledges them.
"""

import argparse
import logging
import sys
from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists, NotFound


def callback(message):
    """Callback function executed whenever a new message is received."""
    try:
        # Decode binary data to string
        payload_str = message.data.decode("utf-8")
        logging.info(f"Received message ID: {message.message_id} | Payload: {payload_str}")

        # Acknowledge receipt of the message
        message.ack()
    except Exception as e:
        logging.error(f"Error processing message {message.message_id}: {e}")
        # Nack the message so Pub/Sub will redeliver it
        message.nack()


def subscribe_telemetry(project_id, subscription_name, topic_name):
    """Subscribes to the Pub/Sub subscription and listens for messages indefinitely."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)

    # Attempt to create the subscription automatically if a topic is provided
    if topic_name:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)
        try:
            subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path}
            )
            logging.info(f"Created subscription: {subscription_path} bound to topic: {topic_path}")
        except AlreadyExists:
            logging.info(f"Subscription already exists: {subscription_path}")
        except NotFound:
            logging.error(
                f"Topic {topic_path} not found. Cannot create subscription. "
                "Ensure the topic exists and the name is correct."
            )
            sys.exit(1)
        except Exception as e:
            logging.warning(
                f"Could not check/create subscription {subscription_path} automatically. "
                f"Will attempt to subscribe assuming it exists. Error: {e}"
            )
    else:
        logging.info(f"Connecting to existing subscription: {subscription_path}")

    # Subscribe and register the callback function
    logging.info(f"Listening for messages on {subscription_path}... Press Ctrl+C to stop.")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    # Keep the main thread alive to receive messages asynchronously
    try:
        # result() blocks indefinitely unless timeout or exception occurs
        streaming_pull_future.result()
    except KeyboardInterrupt:
        # Gracefully shut down on Ctrl+C
        streaming_pull_future.cancel()
        logging.info("Subscriber stopped by user.")
    except Exception as e:
        logging.error(f"Subscriber exited with error: {e}")
        streaming_pull_future.cancel()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    parser = argparse.ArgumentParser(description="Lab 2: Subscribe and print IoT Pub/Sub Telemetry")
    parser.add_argument(
        "--project",
        required=True,
        help="GCP Project ID"
    )
    parser.add_argument(
        "--subscription",
        default="lab2-sub",
        help="Pub/Sub Subscription name (default: lab2-sub)"
    )
    parser.add_argument(
        "--topic",
        default="lab2-topic",
        help="Associated Pub/Sub Topic name (needed to create subscription if it doesn't exist)"
    )

    args = parser.parse_args()
    subscribe_telemetry(args.project, args.subscription, args.topic)
