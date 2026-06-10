"""
Mock Events Publisher for Capstone Project.
Generates simulated sales, inventory updates, and customer updates, 
and publishes them to Google Cloud Pub/Sub topics.
"""

import argparse
import json
import logging
import random
import time
from datetime import datetime
from google.cloud import pubsub_v1

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

PRODUCT_LIST = ["PROD_IPHONE15", "PROD_MACBOOK_AIR", "PROD_GALAXY_S24", "PROD_SONY_WH1000", "PROD_NINTENDO_SWITCH", "PROD_IPAD_PRO"]
STORE_LIST = [f"STORE_{i}" for i in range(1, 20)]
CUSTOMER_TIERS = ["BRONZE", "SILVER", "GOLD", "PLATINUM"]

def generate_order(order_id_seq):
    order_id = f"ORD{1000 + order_id_seq}"
    customer_id = f"CUST{random.randint(100, 999)}"
    product_id = random.choice(PRODUCT_LIST)
    store_id = random.choice(STORE_LIST)
    quantity = random.randint(1, 3)
    price = round(random.uniform(50.0, 1500.0), 2)
    status = random.choices(["COMPLETED", "RETURNED", "CANCELLED"], weights=[0.90, 0.07, 0.03])[0]
    
    return {
        "order_id": order_id,
        "store_id": store_id,
        "product_id": product_id,
        "quantity": quantity,
        "price": price,
        "customer_id": customer_id,
        "event_time": datetime.utcnow().isoformat() + "Z",
        "status": status
    }

def generate_inventory():
    product_id = random.choice(PRODUCT_LIST)
    store_id = random.choice(STORE_LIST)
    quantity_on_hand = random.randint(0, 100)
    supplier_id = f"SUPPLIER_{random.randint(1, 5)}"
    
    return {
        "store_id": store_id,
        "product_id": product_id,
        "quantity_on_hand": quantity_on_hand,
        "last_restocked": datetime.utcnow().isoformat() + "Z",
        "supplier_id": supplier_id,
        "event_time": datetime.utcnow().isoformat() + "Z"
    }

def generate_customer():
    customer_id = f"CUST{random.randint(100, 999)}"
    first_name = random.choice(["John", "Jane", "Alice", "Bob", "Charlie", "David", "Emma", "Frank"])
    last_name = random.choice(["Smith", "Doe", "Johnson", "Brown", "Miller", "Davis", "Garcia", "Rodriguez"])
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    phone = f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
    loyalty_tier = random.choice(CUSTOMER_TIERS)
    
    return {
        "customer_id": customer_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "loyalty_tier": loyalty_tier,
        "signup_date": "2026-06-10",
        "event_time": datetime.utcnow().isoformat() + "Z"
    }

def main():
    parser = argparse.ArgumentParser(description="Publish mock retail events to Pub/Sub")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between event groups in seconds")
    args = parser.parse_known_args()[0]

    publisher = pubsub_v1.PublisherClient()
    
    # Define topic paths
    order_topic = publisher.topic_path(args.project, "orders-events")
    inventory_topic = publisher.topic_path(args.project, "inventory-events")
    customer_topic = publisher.topic_path(args.project, "customer-events")
    
    logging.info("Starting retail mock events publisher...")
    logging.info(f"  Target Project ID : {args.project}")
    logging.info(f"  Publishing Interval: {args.interval}s")
    
    order_seq = 1
    
    try:
        while True:
            # Generate and publish Order Event
            order_data = generate_order(order_seq)
            publisher.publish(order_topic, json.dumps(order_data).encode("utf-8"))
            logging.info(f"Published Order: {order_data['order_id']} | Product: {order_data['product_id']}")
            order_seq += 1
            
            # 50% chance to also publish Inventory Event
            if random.random() > 0.5:
                inventory_data = generate_inventory()
                publisher.publish(inventory_topic, json.dumps(inventory_data).encode("utf-8"))
                logging.info(f"Published Inventory Update: Store: {inventory_data['store_id']} | Product: {inventory_data['product_id']}")
            
            # 20% chance to also publish Customer Event
            if random.random() > 0.8:
                customer_data = generate_customer()
                publisher.publish(customer_topic, json.dumps(customer_data).encode("utf-8"))
                logging.info(f"Published Customer Update: {customer_data['customer_id']} ({customer_data['loyalty_tier']})")
                
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        logging.info("Publisher stopped by user.")

if __name__ == "__main__":
    main()
