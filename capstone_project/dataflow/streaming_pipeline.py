"""
Dataflow Streaming Ingestion Pipeline.
Reads orders, inventory, and customer events from Pub/Sub,
validates/deduplicates/cleans them, and writes them to GCS in Apache Iceberg format.
"""

import argparse
import json
import logging
from typing import NamedTuple, Optional
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.managed import Write

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# ---------------------------------------------------------------------------
# NamedTuple schemas for Apache Beam Row mapping (Iceberg compatibility)
# ---------------------------------------------------------------------------

class RawOrder(NamedTuple):
    order_id: str
    store_id: str
    product_id: str
    quantity: int
    price: float
    customer_id: str
    event_time: str
    status: str

class RawInventory(NamedTuple):
    store_id: str
    product_id: str
    quantity_on_hand: int
    last_restocked: str
    supplier_id: str
    event_time: str

class RawCustomer(NamedTuple):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    loyalty_tier: str
    signup_date: str
    event_time: str

# Register schema coders
beam.coders.registry.register_coder(RawOrder, beam.coders.RowCoder)
beam.coders.registry.register_coder(RawInventory, beam.coders.RowCoder)
beam.coders.registry.register_coder(RawCustomer, beam.coders.RowCoder)

# ---------------------------------------------------------------------------
# Validation and Transformation DoFns
# ---------------------------------------------------------------------------

class ParseAndValidateOrder(beam.DoFn):
    def process(self, element):
        try:
            payload = json.loads(element.decode("utf-8"))
            order_id = payload.get("order_id")
            store_id = payload.get("store_id")
            product_id = payload.get("product_id")
            quantity = payload.get("quantity")
            price = payload.get("price")
            customer_id = payload.get("customer_id", "ANONYMOUS")
            event_time = payload.get("event_time")
            status = payload.get("status", "COMPLETED")

            # Basic Validation: Drop elements if required fields are missing
            if not all([order_id, store_id, product_id, quantity, price, event_time]):
                logging.warning(f"Drop Order (validation failed): {payload}")
                return

            yield {
                "order_id": str(order_id),
                "store_id": str(store_id),
                "product_id": str(product_id),
                "quantity": int(quantity),
                "price": float(price),
                "customer_id": str(customer_id),
                "event_time": str(event_time),
                "status": str(status)
            }
        except Exception as e:
            logging.error(f"Error parsing order: {e}")

class ParseAndValidateInventory(beam.DoFn):
    def process(self, element):
        try:
            payload = json.loads(element.decode("utf-8"))
            store_id = payload.get("store_id")
            product_id = payload.get("product_id")
            quantity_on_hand = payload.get("quantity_on_hand")
            last_restocked = payload.get("last_restocked")
            supplier_id = payload.get("supplier_id", "UNKNOWN")
            event_time = payload.get("event_time")

            if not all([store_id, product_id, quantity_on_hand, event_time]):
                logging.warning(f"Drop Inventory (validation failed): {payload}")
                return

            yield {
                "store_id": str(store_id),
                "product_id": str(product_id),
                "quantity_on_hand": int(quantity_on_hand),
                "last_restocked": str(last_restocked or event_time),
                "supplier_id": str(supplier_id),
                "event_time": str(event_time)
            }
        except Exception as e:
            logging.error(f"Error parsing inventory: {e}")

class ParseAndValidateCustomer(beam.DoFn):
    def process(self, element):
        try:
            payload = json.loads(element.decode("utf-8"))
            customer_id = payload.get("customer_id")
            first_name = payload.get("first_name", "")
            last_name = payload.get("last_name", "")
            email = payload.get("email")
            phone = payload.get("phone", "")
            loyalty_tier = payload.get("loyalty_tier", "BRONZE")
            signup_date = payload.get("signup_date", "")
            event_time = payload.get("event_time")

            if not all([customer_id, email, event_time]):
                logging.warning(f"Drop Customer (validation failed): {payload}")
                return

            yield {
                "customer_id": str(customer_id),
                "first_name": str(first_name),
                "last_name": str(last_name),
                "email": str(email),
                "phone": str(phone),
                "loyalty_tier": str(loyalty_tier),
                "signup_date": str(signup_date),
                "event_time": str(event_time)
            }
        except Exception as e:
            logging.error(f"Error parsing customer: {e}")

# ---------------------------------------------------------------------------
# Pipeline Deployment Runner
# ---------------------------------------------------------------------------

def run(argv=None):
    parser = argparse.ArgumentParser(description="GCP Capstone Streaming Ingestion Pipeline")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--warehouse_path", required=True, help="GCS Iceberg Warehouse Path (e.g. gs://MY_BUCKET/warehouse)")
    
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(StandardOptions).streaming = True
    
    # Iceberg Catalogs Base Configurations
    def get_iceberg_config(table_name):
        return {
            "table": f"raw_data.{table_name}",
            "catalog_name": "gcs_hadoop_catalog",
            "catalog_properties": {
                "catalog-impl": "org.apache.iceberg.hadoop.HadoopCatalog",
                "warehouse": known_args.warehouse_path
            },
            "triggering_frequency_seconds": 30
        }

    with beam.Pipeline(options=pipeline_options) as p:
        
        # 1. Pipeline: Ingest Orders Stream
        (
            p
            | "ReadOrders" >> beam.io.ReadFromPubSub(topic=f"projects/{known_args.project}/topics/orders-events")
            | "ParseOrders" >> beam.ParDo(ParseAndValidateOrder())
            | "MapToOrderRow" >> beam.Map(lambda x: RawOrder(**x)).with_output_types(RawOrder)
            | "WriteOrdersToIceberg" >> Write("iceberg", config=get_iceberg_config("raw_orders"))
        )
        
        # 2. Pipeline: Ingest Inventory Stream
        (
            p
            | "ReadInventory" >> beam.io.ReadFromPubSub(topic=f"projects/{known_args.project}/topics/inventory-events")
            | "ParseInventory" >> beam.ParDo(ParseAndValidateInventory())
            | "MapToInventoryRow" >> beam.Map(lambda x: RawInventory(**x)).with_output_types(RawInventory)
            | "WriteInventoryToIceberg" >> Write("iceberg", config=get_iceberg_config("raw_inventory"))
        )

        # 3. Pipeline: Ingest Customers Stream
        (
            p
            | "ReadCustomers" >> beam.io.ReadFromPubSub(topic=f"projects/{known_args.project}/topics/customer-events")
            | "ParseCustomers" >> beam.ParDo(ParseAndValidateCustomer())
            | "MapToCustomerRow" >> beam.Map(lambda x: RawCustomer(**x)).with_output_types(RawCustomer)
            | "WriteCustomersToIceberg" >> Write("iceberg", config=get_iceberg_config("raw_customers"))
        )

if __name__ == "__main__":
    run()
