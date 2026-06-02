import argparse
import time
from google.cloud import pubsub_v1

def callback(message):
    """Callback function to process received messages."""
    print(f"Received message ID: {message.message_id}")
    try:
        # Decode the payload (Spark Structured Streaming outputs bytes)
        data_str = message.data.decode('utf-8')
        print(f"Data: {data_str}")
    except Exception as e:
        print(f"Failed to decode message: {e}")
        
    print("-" * 40)
    # Acknowledge the message so it's not redelivered
    message.ack()

def consume_messages(project_id, subscription_name):
    """Subscribes to a Pub/Sub subscription and prints messages."""
    
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)

    print(f"Listening for messages on {subscription_path}...\n")
    print("Waiting for Spark to process and publish data (this may take a minute or two).")
    print("-" * 50)

    # Subscribe to the topic
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    # Wrap subscriber in a 'with' block to automatically call close() when done
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result()
        except KeyboardInterrupt:
            print("\nConsumer stopped by user.")
            streaming_pull_future.cancel()
        except Exception as e:
            print(f"Listening raised an error: {e}")
            streaming_pull_future.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pub/Sub Output Consumer")
    parser.add_argument("--project_id", required=True, help="Google Cloud Project ID")
    parser.add_argument("--subscription", required=True, help="Pub/Sub Subscription Name")
    
    args = parser.parse_args()
    consume_messages(args.project_id, args.subscription)
