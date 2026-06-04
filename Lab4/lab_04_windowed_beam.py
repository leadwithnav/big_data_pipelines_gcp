#!/usr/bin/env python
"""
Lab 4: Apache Beam Windowed Streaming Pipeline on Google Cloud Dataflow

This pipeline demonstrates:
1. Reading messages from a Pub/Sub input topic
2. Parsing JSON, keying by device_id, and assigning event-time timestamps from the payload
3. Windowing elements into fixed-duration windows (default 60 seconds)
4. Aggregating values per-key (calculating count and average temp/humidity)
5. Extracting window metadata (window start/end) using DoFn.WindowParam
6. Writing the JSON-serialized aggregates to an output Pub/Sub topic

Run with:
    python lab_04_windowed_beam.py \
        --project=YOUR_PROJECT_ID \
        --region=us-central1 \
        --input_topic=projects/YOUR_PROJECT_ID/topics/iot-raw \
        --output_topic=projects/YOUR_PROJECT_ID/topics/iot-aggregated \
        --temp_location=gs://YOUR_PROJECT_ID-dataflow-temp/temp \
        --staging_location=gs://YOUR_PROJECT_ID-dataflow-temp/staging \
        --runner=DataflowRunner \
        --streaming
"""

import argparse
import json
import logging
from datetime import datetime, timezone
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam import window


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
            # Decode Pub/Sub bytes to string, then parse JSON
            payload = json.loads(element.decode("utf-8"))
            
            # Extract timestamp string (e.g. "2026-06-04T12:28:16.123456+00:00")
            timestamp_str = payload.get("timestamp")
            device_id = payload.get("device_id")
            
            if not timestamp_str or not device_id:
                logging.warning(f"Skipping malformed payload (missing fields): {payload}")
                return

            # Convert ISO 8601 string to unix timestamp (seconds)
            # Replacing 'Z' with '+00:00' to handle standard ISO timezone designators safely
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            unix_timestamp = dt.timestamp()

            # Output the key-value pair wrapped with its event timestamp
            yield beam.window.TimestampedValue((device_id, payload), unix_timestamp)

        except Exception as e:
            logging.error(f"Error parsing/timestamping element {element}: {e}", exc_info=True)


class AggregateTelemetryFn(beam.DoFn):
    """
    Aggregates telemetry records grouped by device_id in a given time window.
    Calculates average temperature, average humidity, and total reading counts.
    Accesses the current window boundaries using WindowParam.
    """

    def process(self, element, window=beam.DoFn.WindowParam):
        device_id, readings = element

        # Extract temperature and humidity readings
        temps = [r["temperature"] for r in readings if "temperature" in r]
        hums = [r["humidity"] for r in readings if "humidity" in r]
        statuses = [r["status"] for r in readings if "status" in r]

        if not temps:
            return

        # Calculate statistics
        avg_temp = sum(temps) / len(temps)
        avg_hum = sum(hums) / len(hums) if hums else 0.0
        error_count = sum(1 for status in statuses if status == "ERROR")

        # Convert window boundaries to UTC ISO-8601 strings
        window_start = window.start.to_utc_datetime().isoformat()
        window_end = window.end.to_utc_datetime().isoformat()

        # Build output aggregate payload
        result = {
            "device_id": device_id,
            "window_start": window_start,
            "window_end": window_end,
            "avg_temperature": round(avg_temp, 2),
            "avg_humidity": round(avg_hum, 2),
            "reading_count": len(readings),
            "error_count": error_count,
            "aggregated_at": datetime.now(timezone.utc).isoformat()
        }

        # Encode and yield
        yield json.dumps(result).encode("utf-8")


# ---------------------------------------------------------------------------
# Pipeline definition
# ---------------------------------------------------------------------------

def run(argv=None):
    parser = argparse.ArgumentParser(description="Lab 4: Windowed Beam Streaming Pipeline")

    # Custom arguments for our pipeline
    parser.add_argument(
        "--input_topic",
        required=True,
        help="Full Pub/Sub input topic path: projects/PROJECT_ID/topics/TOPIC_NAME",
    )
    parser.add_argument(
        "--output_topic",
        required=True,
        help="Full Pub/Sub output topic path: projects/PROJECT_ID/topics/TOPIC_NAME",
    )
    parser.add_argument(
        "--window_duration",
        type=int,
        default=60,
        help="Duration of the fixed time window in seconds (default: 60)",
    )

    # Parse arguments
    known_args, pipeline_args = parser.parse_known_args(argv)

    # Instantiate pipeline options (includes staging, runner, project etc.)
    pipeline_options = PipelineOptions(pipeline_args)

    # Streaming pipelines must have the streaming option explicitly set
    pipeline_options.view_as(StandardOptions).streaming = True

    logging.info("Starting Lab 4 Windowed streaming pipeline...")
    logging.info(f"  Input topic     : {known_args.input_topic}")
    logging.info(f"  Output topic    : {known_args.output_topic}")
    logging.info(f"  Window duration : {known_args.window_duration} seconds")

    # Build and run the pipeline
    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            # 1. Read raw bytes from the input topic
            | "ReadFromPubSub"     >> beam.io.ReadFromPubSub(topic=known_args.input_topic)

            # 2. Parse JSON bytes to dictionary, set custom event timestamp, and key by device_id
            | "ParseAndTimestamp"  >> beam.ParDo(ParseAndTimestampFn())

            # 3. Apply Fixed Windows
            | "ApplyFixedWindows"  >> beam.WindowInto(window.FixedWindows(known_args.window_duration))

            # 4. Group elements of the same key (device_id) within the window
            | "GroupPerDevice"     >> beam.GroupByKey()

            # 5. Compute telemetry aggregates and attach window metadata
            | "AggregateTelemetry" >> beam.ParDo(AggregateTelemetryFn())

            # 6. Write JSON bytes to the output Pub/Sub topic
            | "WriteToPubSub"      >> beam.io.WriteToPubSub(topic=known_args.output_topic)
        )

    logging.info("Pipeline submitted to Dataflow. Monitor progress in the GCP Console.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    run()
