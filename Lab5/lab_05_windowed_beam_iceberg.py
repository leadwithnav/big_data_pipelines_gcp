#!/usr/bin/env python
"""
Lab 5: Apache Beam Windowed Streaming Pipeline to Apache Iceberg on GCS

This pipeline demonstrates:
1. Reading streaming messages from a Pub/Sub input topic
2. Parsing JSON, setting custom event timestamps, and windowing (60s fixed windows)
3. Grouping and calculating telemetry aggregates per device
4. Mapping aggregates to a schema-aware Python NamedTuple structure
5. Using Apache Beam's Managed I/O API to write to an Apache Iceberg table on GCS 
   using a Hadoop Catalog (org.apache.iceberg.hadoop.HadoopCatalog)

Run with:
    python lab_05_windowed_beam_iceberg.py \
        --project=YOUR_PROJECT_ID \
        --region=us-central1 \
        --input_topic=projects/YOUR_PROJECT_ID/topics/iot-raw \
        --warehouse_path=gs://YOUR_BUCKET_NAME/warehouse \
        --temp_location=gs://YOUR_BUCKET_NAME/temp \
        --staging_location=gs://YOUR_BUCKET_NAME/staging \
        --runner=DataflowRunner \
        --streaming
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from typing import NamedTuple

import apache_beam as beam
from apache_beam import window
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.managed import Write

# ---------------------------------------------------------------------------
# Schema Definition (Row structure for Apache Iceberg)
# ---------------------------------------------------------------------------

class SensorAggregate(NamedTuple):
    device_id: str
    window_start: str
    window_end: str
    avg_temperature: float
    avg_humidity: float
    reading_count: int
    error_count: int
    aggregated_at: str

# Register the NamedTuple with RowCoder so Beam treats it as a schema-aware Row type
beam.coders.registry.register_coder(SensorAggregate, beam.coders.RowCoder)


# ---------------------------------------------------------------------------
# Custom DoFns
# ---------------------------------------------------------------------------

class ParseAndTimestampFn(beam.DoFn):
    """
    Parses incoming raw bytes into JSON, keys the elements by device_id,
    and assigns custom event timestamps extracted from the message payload.
    """

    def process(self, element):
        try:
            payload = json.loads(element.decode("utf-8"))
            timestamp_str = payload.get("timestamp")
            device_id = payload.get("device_id")
            
            if not timestamp_str or not device_id:
                logging.warning(f"Skipping malformed payload (missing fields): {payload}")
                return

            # Parse timestamp and convert to unix epoch seconds
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            unix_timestamp = dt.timestamp()

            yield beam.window.TimestampedValue((device_id, payload), unix_timestamp)

        except Exception as e:
            logging.error(f"Error parsing/timestamping element {element}: {e}", exc_info=True)


class AggregateTelemetryFn(beam.DoFn):
    """
    Aggregates telemetry records grouped by device_id in a given time window.
    Yields dictionary payloads representing the aggregated values.
    """

    def process(self, element, window=beam.DoFn.WindowParam):
        device_id, readings = element

        # Extract temperature, humidity, and status
        temps = [r["temperature"] for r in readings if "temperature" in r]
        hums = [r["humidity"] for r in readings if "humidity" in r]
        statuses = [r["status"] for r in readings if "status" in r]

        if not temps:
            return

        # Calculate statistics
        avg_temp = sum(temps) / len(temps)
        avg_hum = sum(hums) / len(hums) if hums else 0.0
        error_count = sum(1 for status in statuses if status == "ERROR")

        window_start = window.start.to_utc_datetime().isoformat()
        window_end = window.end.to_utc_datetime().isoformat()

        # Yield structured dictionary matching SensorAggregate schema
        yield {
            "device_id": str(device_id),
            "window_start": str(window_start),
            "window_end": str(window_end),
            "avg_temperature": float(avg_temp),
            "avg_humidity": float(avg_hum),
            "reading_count": int(len(readings)),
            "error_count": int(error_count),
            "aggregated_at": str(datetime.now(timezone.utc).isoformat())
        }


# ---------------------------------------------------------------------------
# Pipeline definition
# ---------------------------------------------------------------------------

def run(argv=None):
    parser = argparse.ArgumentParser(description="Lab 5: Windowed Beam Streaming Pipeline to Iceberg")

    # Custom arguments
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
    parser.add_argument(
        "--window_duration",
        type=int,
        default=60,
        help="Duration of the fixed time window in seconds (default: 60)",
    )

    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(StandardOptions).streaming = True

    # Setup the Iceberg Managed I/O Configuration with Hadoop Catalog on GCS
    iceberg_config = {
        "table": "sensor_db.aggregates",
        "catalog_name": "gcs_hadoop_catalog",
        "catalog_properties": {
            "catalog-impl": "org.apache.iceberg.hadoop.HadoopCatalog",
            "warehouse": known_args.warehouse_path
        }
    }

    logging.info("Starting Lab 5 Windowed streaming pipeline (Beam to Iceberg)...")
    logging.info(f"  Input topic      : {known_args.input_topic}")
    logging.info(f"  Iceberg Warehouse: {known_args.warehouse_path}")
    logging.info(f"  Window duration  : {known_args.window_duration} seconds")

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            # 1. Read bytes from Pub/Sub
            | "ReadFromPubSub"     >> beam.io.ReadFromPubSub(topic=known_args.input_topic)

            # 2. Parse JSON, assign timestamps, and key by device_id
            | "ParseAndTimestamp"  >> beam.ParDo(ParseAndTimestampFn())

            # 3. Apply Fixed Windows
            | "ApplyFixedWindows"  >> beam.WindowInto(window.FixedWindows(known_args.window_duration))

            # 4. Group elements by device key within the window
            | "GroupPerDevice"     >> beam.GroupByKey()

            # 5. Compute telemetry aggregates
            | "AggregateTelemetry" >> beam.ParDo(AggregateTelemetryFn())

            # 6. Map to NamedTuple schema-aware objects
            | "MapToRow"           >> beam.Map(lambda x: SensorAggregate(**x)).with_output_types(SensorAggregate)

            # 7. Write to Apache Iceberg table on GCS using Managed I/O
            | "WriteToIceberg"     >> Write("iceberg", config=iceberg_config)
        )

    logging.info("Pipeline submitted to Dataflow. Monitor progress in the GCP Console.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    run()
