"""
Lab 3: Apache Beam Streaming Pipeline on Google Cloud Dataflow

This pipeline demonstrates:
1. Reading messages from a Pub/Sub input topic
2. Decoding the bytes to a string
3. Applying a simple transformation (convert to UPPERCASE)
4. Encoding the result back to bytes
5. Writing the result to a Pub/Sub output topic

Run with:
    python lab_03_dataflow.py \\
        --project=YOUR_PROJECT_ID \\
        --region=us-central1 \\
        --input_topic=projects/YOUR_PROJECT_ID/topics/beam-input \\
        --output_topic=projects/YOUR_PROJECT_ID/topics/beam-output \\
        --temp_location=gs://YOUR_PROJECT_ID-dataflow-temp/temp \\
        --staging_location=gs://YOUR_PROJECT_ID-dataflow-temp/staging \\
        --runner=DataflowRunner \\
        --streaming
"""

import argparse
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions


# ---------------------------------------------------------------------------
# Custom DoFn: transformation logic lives here
# ---------------------------------------------------------------------------

class UpperCaseFn(beam.DoFn):
    """
    A simple DoFn that:
    - Receives a message as bytes from Pub/Sub
    - Decodes it to a UTF-8 string
    - Converts it to UPPERCASE
    - Logs the result
    - Yields the result encoded back to bytes (ready to write to Pub/Sub)
    """

    def process(self, element):
        # Decode bytes → string
        message = element.decode("utf-8")
        logging.info(f"Received message: {message}")

        # Transform: convert to UPPERCASE
        transformed = message.upper()
        logging.info(f"Transformed message: {transformed}")

        # Encode string → bytes and yield
        yield transformed.encode("utf-8")


# ---------------------------------------------------------------------------
# Pipeline definition
# ---------------------------------------------------------------------------

def run(argv=None):
    parser = argparse.ArgumentParser(description="Lab 3: Beam Pub/Sub to Pub/Sub Pipeline")

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

    # Parse our custom args; pass the remainder to Beam PipelineOptions
    known_args, pipeline_args = parser.parse_known_args(argv)

    # Build PipelineOptions from the remaining args (includes --runner, --project, etc.)
    pipeline_options = PipelineOptions(pipeline_args)

    # IMPORTANT: Mark the pipeline as streaming so Beam keeps it running indefinitely
    pipeline_options.view_as(StandardOptions).streaming = True

    logging.info("Starting Lab 3 Beam pipeline...")
    logging.info(f"  Input topic  : {known_args.input_topic}")
    logging.info(f"  Output topic : {known_args.output_topic}")

    # Build and run the pipeline
    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            # Step 1: Read raw bytes from Pub/Sub
            | "ReadFromPubSub"   >> beam.io.ReadFromPubSub(topic=known_args.input_topic)

            # Step 2: Apply transformation (uppercase)
            | "TransformToUpper" >> beam.ParDo(UpperCaseFn())

            # Step 3: Write bytes to output Pub/Sub topic
            | "WriteToPubSub"    >> beam.io.WriteToPubSub(topic=known_args.output_topic)
        )

    logging.info("Pipeline submitted to Dataflow. Monitor progress in the GCP Console.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    run()
