# Architecture Explanation: Walmart GCP Retail Big Data Pipeline

This document provides a deep dive into the design decisions, component choices, and operational optimizations implemented in the Walmart GCP Retail Big Data Pipeline.

---

## 1. System Architecture Overview

The pipeline implements an end-to-end real-time ingestion and batch consolidation architecture:

```
[Walmart Stores / Web / App]
              │
              │ (Sales, Inventory, Customer Events)
              ▼
    ┌───────────────────┐
    │  Pub/Sub Topics   │ <── Ingestion Backbone (orders, inventory, customer topics)
    └─────────┬─────────┘
              │ (Streaming event streams)
              ▼
    ┌───────────────────┐
    │  Dataflow (Beam)  │ <── Schema validation, deduplication, late data tagging
    └─────────┬─────────┘
              │ (Streaming append writes)
              ▼
    ┌───────────────────┐
    │  Raw GCS Iceberg  │ <── ACID raw tables on Cloud Storage (Hadoop Catalog)
    └─────────┬─────────┘
              │
              │ (Nightly Orchestrated ETL)
              ▼
    ┌───────────────────┐
    │  Dataproc Spark   │ <── Joins, aggregates, deduplications & MERGE updates
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ Curated GCS Ice   │ <── Curated business tables (sales_daily, inventory_by_store, customer_360)
    └─────────┬─────────┘
              │
              │ (Zero-copy sync via BigQuery External Tables)
              ▼
    ┌───────────────────┐
    │     BigQuery      │ <── Analytical layer, BI reports, Quality Assertions
    └───────────────────┘

   ========================================================================
   Orchestration Layer: Apache Airflow (Cloud Composer)
   - Provisions ephemeral Dataproc clusters (saving compute costs)
   - Runs PySpark ETL batch job and refreshes BigQuery tables
   - Executes Iceberg maintenance: File Compaction & Snapshot Expiration
   ========================================================================
```

---

## 2. Architectural Components & Design Rationale

### A. Ingestion Layer: Google Cloud Pub/Sub
- **Role**: Serves as the high-throughput, horizontally scalable messaging backbone.
- **Why Pub/Sub?**
  - **Decoupling**: Decouples producer systems (POS systems, website transactions, mobile app logs) from processing downstream systems.
  - **Scale**: Seamlessly handles millions of events per second with zero administrative overhead.
  - **Buffer**: acts as a backpressure buffer, retaining messages for up to 7 days if downstream consumers undergo downtime or maintenance.

### B. Streaming Processing: Google Cloud Dataflow (Apache Beam)
- **Role**: Consumes messages from Pub/Sub in real-time, performs validation, maps them to structured rows, and writes to raw GCS Iceberg tables.
- **Why Dataflow?**
  - **Serverless**: Automatically scales workers up or down based on stream volume.
  - **Schema Validation**: Evaluates incoming payloads against strict schemas (defined in the `schemas/` directory), routing invalid records to a dead-letter queue or logging errors.
  - **Streaming Iceberg Sink**: Beam's Managed I/O Iceberg connector (`Write("iceberg", ...)`) enables write operations directly from the stream into GCS using the Hadoop Catalog.

### C. Storage Format: Apache Iceberg on Google Cloud Storage (GCS)
- **Role**: Provides the table format for both the Raw and Curated layers in GCS.
- **Why Iceberg over standard Parquet/CSV?**
  - **ACID Transactions**: Multiple writers (Dataflow streams) and readers (Dataproc Spark jobs) can access the data concurrently without dirty reads or lockouts.
  - **Late-Data Handling**: In retail, store networks can drop offline. If a store uploads historical data, Iceberg safely inserts it into the correct partition (e.g., historical date partition) without rewrites or table corruption.
  - **Time Travel & Rollback**: Enables querying the table at a specific historical point in time or snapshot ID.
  - **Schema & Partition Evolution**: Modifying column names, adding fields, or changing partition layouts doesn't require rewriting historical data.

### D. Processing Engine: Dataproc PySpark (Batch ETL)
- **Role**: Performs heavy, cost-efficient joins, window-aggregations, and deduplications on raw tables, and writes results to the curated layer.
- **Why Dataproc?**
  - **MERGE INTO Support**: Utilizes Iceberg's ACID properties to apply upsert changes (e.g., merging inventory updates or updating customer profiles) using Spark SQL `MERGE INTO` semantics.
  - **Cost-Efficiency**: Orchestrated as an ephemeral cluster that exists only for the duration of the ETL job, shutting down immediately after completion to minimize costs.

### E. Analytics Layer: Google BigQuery
- **Role**: Serves as the query and visualization backend for BI dashboards and executive reports.
- **Why BigQuery?**
  - **BigQuery External Tables for Iceberg**: Allows querying GCS Iceberg tables directly from BigQuery without duplicating data or incurring storage fees twice (Zero-Copy architecture).
  - **Serverless Analytics**: Runs SQL queries over terabytes of data in seconds.

### F. Orchestration: Apache Airflow (Cloud Composer)
- **Role**: Schedules, triggers, and monitors the entire end-to-end data pipeline.
- **Why Airflow?**
  - **Dependency Management**: Ensures that the Spark ETL job only runs after the Dataproc cluster is successfully created, and that BigQuery tables are refreshed only after the ETL successfully completes.
  - **Automated Iceberg Maintenance**: Orchestrates crucial maintenance tasks—compaction (rewriting manifest files and merging small files) and snapshot expiration (deleting snapshots older than 7 days)—ensuring query speeds remain high and storage costs low.

---

## 3. Resolving Critical Production Blockers

During implementation and testing, several subtle but critical runtime blockers were addressed to ensure production stability:

### Blocker 1: Iceberg Catalog Properties Conflict in PySpark
- **Issue**: Attempting to configure Iceberg in Spark by passing both `spark.sql.catalog.<name>.type` and `spark.sql.catalog.<name>.catalog-impl` throws an `IllegalArgumentException` stating that both properties cannot be set simultaneously.
- **Resolution**: When using Iceberg's custom `HadoopCatalog`, set **only** `catalog-impl` to `org.apache.iceberg.hadoop.HadoopCatalog` and omit `type` entirely.

### Blocker 2: Spark ClassCastException in YARN Distributed Workers
- **Issue**: When running a PySpark script on Dataproc in YARN client/cluster mode, reading Iceberg tables failed on executors with a `ClassCastException` (e.g., failed to serialize proxy partition lists). This occurred because the Iceberg runtime JAR was only present on the Master node's classpath.
- **Resolution**: Enabled GCS-scoped jar distribution. The Dataproc cluster is provisioned with the property `spark:spark.jars` pointing to the GCS path of the Iceberg runtime JAR (`gs://[PROJECT_ID]-code-bin/libs/iceberg-spark-runtime-3.5_2.12-1.5.2.jar`). YARN distributes the JAR to all worker node executors automatically.

### Blocker 3: YARN ApplicationMaster Cache Invalidation
- **Issue**: In YARN client mode, calling `spark.stop()` at the end of a Spark ETL script kills the ApplicationMaster (AM) registration cache. Running another Spark script on the same session shortly after throws an `InvalidApplicationMasterRequestException`.
- **Resolution**: The Airflow DAG handles this by spinning up ephemeral clusters for isolated tasks, and Python Spark operations utilize `SparkSession.builder.getOrCreate()` and shutdown hooks rather than abrupt execution stops where lifecycle management is handled by YARN.

### Blocker 4: Path Parsing URISyntaxException
- **Issue**: Deploying Spark configurations with unexpanded env variables (e.g. `gs://${GCP_PROJECT}-iceberg-raw/`) resulted in invalid paths (e.g. `gs://-iceberg-raw/`) when variables were empty, throwing a `URISyntaxException`.
- **Resolution**: Fully resolved paths by retrieving active project configurations via Google credentials (`google.auth.default()`) and `gcloud config` in scripts, and using environment checks in Airflow and Terraform.
