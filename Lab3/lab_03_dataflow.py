"""
Lab 3: Apache Beam Streaming Pipeline to Apache Iceberg on GCS

This pipeline demonstrates:
1. Reading streaming telemetry messages from a Pub/Sub input topic.
2. Parsing JSON, and filtering telemetry records (keeping only status == "OK").
3. Mapping the filtered telemetry to a schema-aware Python NamedTuple structure.
4. Using Apache Beam's Managed I/O API to write the data to an Apache Iceberg table on GCS 
   using a Hadoop Catalog (org.apache.iceberg.hadoop.HadoopCatalog).

Run with:
    python lab_03_dataflow.py \
        --project=YOUR_PROJECT_ID \
        --region=us-central1 \
        --input_topic=projects/YOUR_PROJECT_ID/topics/beam-input \
        --warehouse_path=gs://YOUR_BUCKET_NAME/warehouse \
        --temp_location=gs://YOUR_BUCKET_NAME/temp \
        --staging_location=gs://YOUR_BUCKET_NAME/staging \
        --runner=DataflowRunner \
        --streaming
"""

import argparse
import json
import logging
from typing import NamedTuple

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.managed import Write

# ---------------------------------------------------------------------------
# Schema Definition (Row structure for Apache Iceberg)
# ---------------------------------------------------------------------------

class SensorReading(NamedTuple):
    device_id: str
    temperature: float
    humidity: float
    status: str
    timestamp: str

# Register the NamedTuple with RowCoder so Beam treats it as a schema-aware Row type
beam.coders.registry.register_coder(SensorReading, beam.coders.RowCoder)


# ---------------------------------------------------------------------------
# Custom DoFn: parsing, filtering, and mapping logic
# ---------------------------------------------------------------------------

class ParseAndFilterFn(beam.DoFn):
    """
    Parses incoming raw bytes into JSON, filters out records that do not have 
    a status of "OK" (i.e. filters out "ERROR" states), and maps the payload 
    to a SensorReading NamedTuple.
    """

    def process(self, element):
        try:
            payload = json.loads(element.decode("utf-8"))
            device_id = payload.get("device_id")
            temperature = payload.get("temperature")
            humidity = payload.get("humidity")
            status = payload.get("status")
            timestamp = payload.get("timestamp")

            if not device_id or status is None:
                logging.warning(f"Skipping malformed payload (missing fields): {payload}")
                return

            # Filtering logic: Only keep records with status "OK"
            if status == "OK":
                yield SensorReading(
                    device_id=str(device_id),
                    temperature=float(temperature),
                    humidity=float(humidity),
                    status=str(status),
                    timestamp=str(timestamp)
                )
            else:
                logging.debug(f"Filtered out record with status {status}: {payload}")

        except Exception as e:
            logging.error(f"Error parsing/filtering element {element}: {e}", exc_info=True)


# ---------------------------------------------------------------------------
# Pipeline definition
# ---------------------------------------------------------------------------

def run(argv=None):
    parser = argparse.ArgumentParser(description="Lab 3: Beam Pub/Sub to Iceberg Pipeline")

    # Custom arguments for our pipeline
    parser.add_argument(
        "--input_topic",
        required=True,
        help="Full Pub/Sub input topic path: projects/PROJECT_ID/topics/TOPIC_NAME",
    )
    parser.add_argument(
        "--warehouse_path",
        required=True,
        help="GCS base path for the Iceberg warehouse (e.g. gs://MY_BUCKET/warehouse)",
    )

    # Parse our custom args; pass the remainder to Beam PipelineOptions
    known_args, pipeline_args = parser.parse_known_args(argv)

    # Build PipelineOptions from the remaining args (includes --runner, --project, etc.)
    pipeline_options = PipelineOptions(pipeline_args)

    # IMPORTANT: Mark the pipeline as streaming so Beam keeps it running indefinitely
    pipeline_options.view_as(StandardOptions).streaming = True

    # Setup the Iceberg Managed I/O Configuration with Hadoop Catalog on GCS
    iceberg_config = {
        "table": "sensor_db.filtered_readings",
        "catalog_name": "gcs_hadoop_catalog",
        "catalog_properties": {
            "catalog-impl": "org.apache.iceberg.hadoop.HadoopCatalog",
            "warehouse": known_args.warehouse_path
        }
    }

    logging.info("Starting Lab 3 Beam-to-Iceberg streaming pipeline...")
    logging.info(f"  Input topic      : {known_args.input_topic}")
    logging.info(f"  Iceberg Warehouse: {known_args.warehouse_path}")

    # Build and run the pipeline
    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            # Step 1: Read raw bytes from Pub/Sub
            | "ReadFromPubSub"     >> beam.io.ReadFromPubSub(topic=known_args.input_topic)

            # Step 2: Parse, Filter records where status != "OK", and Map to NamedTuple Row
            | "ParseAndFilter"     >> beam.ParDo(ParseAndFilterFn())

            # Step 3: Write schema-aware Rows to GCS Iceberg Table
            | "WriteToIceberg"     >> Write("iceberg", config=iceberg_config)
        )

    logging.info("Pipeline submitted to Dataflow. Monitor progress in the GCP Console.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    run()
