import argparse
import io
import time
import random
import uuid
import fastavro
from google.cloud import pubsub_v1

# The Avro schema definition provided
schema = {
    "type": "record",
    "name": "Avro",
    "fields": [
        {"name": "orderId", "type": "string"},
        {"name": "amount", "type": "float"},
        {"name": "quantiy", "type": "int"}
    ]
}

parsed_schema = fastavro.parse_schema(schema)

def publish_messages(project_id, topic_name):
    """Publishes streaming order events in Avro format to a Pub/Sub topic."""
    
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    print(f"Publishing Avro order events to {topic_path}...")

    try:
        while True:
            # Generate a mock order
            order = {
                "orderId": str(uuid.uuid4())[:8],
                "amount": round(random.uniform(10.0, 500.0), 2),
                "quantiy": random.randint(1, 10)  # matching the user's schema spelling
            }
            
            # Serialize to Avro binary format
            bytes_writer = io.BytesIO()
            fastavro.schemaless_writer(bytes_writer, parsed_schema, order)
            avro_bytes = bytes_writer.getvalue()
            
            # Publish the message
            future = publisher.publish(topic_path, data=avro_bytes)
            message_id = future.result()
            
            print(f"Published order {order['orderId']} (amount: {order['amount']}, quantiy: {order['quantiy']}) (Message ID: {message_id})")
            
            # Sleep for a short random interval (e.g., 0.5 to 2.0 seconds)
            time.sleep(random.uniform(0.5, 2.0))
            
    except KeyboardInterrupt:
        print("\nPublisher stopped by user.")
    except Exception as e:
        print(f"Error publishing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pub/Sub Avro Publisher")
    parser.add_argument("--project_id", required=True, help="Google Cloud Project ID")
    parser.add_argument("--topic", required=True, help="Pub/Sub Topic Name")
    
    args = parser.parse_args()
    publish_messages(args.project_id, args.topic)
