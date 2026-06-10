"""
Dataproc PySpark Batch ETL Job.
Reads raw Iceberg tables, performs aggregations and joins,
and applies ACID MERGE INTO statements to update curated business tables.
"""

import argparse
from pyspark.sql import SparkSession

def main():
    parser = argparse.ArgumentParser(description="Dataproc Batch PySpark Iceberg ETL Job")
    parser.add_argument("--raw_warehouse", required=True, help="GCS raw Iceberg warehouse GCS path")
    parser.add_argument("--curated_warehouse", required=True, help="GCS curated Iceberg warehouse GCS path")
    args = parser.parse_known_args()[0]

    # Initialize Spark Session with custom catalogs for Raw and Curated Iceberg warehouses
    spark = SparkSession.builder \
        .appName("Walmart-Retail-ETL-Batch-Job") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.raw_cat", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.raw_cat.catalog-impl", "org.apache.iceberg.hadoop.HadoopCatalog") \
        .config("spark.sql.catalog.raw_cat.warehouse", args.raw_warehouse) \
        .config("spark.sql.catalog.curated_cat", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.curated_cat.catalog-impl", "org.apache.iceberg.hadoop.HadoopCatalog") \
        .config("spark.sql.catalog.curated_cat.warehouse", args.curated_warehouse) \
        .getOrCreate()

    # Define raw table paths
    raw_orders = "raw_cat.raw_data.raw_orders"
    raw_inventory = "raw_cat.raw_data.raw_inventory"
    raw_customers = "raw_cat.raw_data.raw_customers"

    # Define curated table paths
    curated_sales_daily = "curated_cat.curated_data.sales_daily"
    curated_inventory_store = "curated_cat.curated_data.inventory_by_store"
    curated_customer_360 = "curated_cat.curated_data.customer_360"
    curated_product_perf = "curated_cat.curated_data.product_performance"

    # Create target curated database if not exists
    spark.sql("CREATE DATABASE IF NOT EXISTS curated_cat.curated_data")

    # -----------------------------------------------------------------------
    # ETL 1: Aggregated Daily Sales (incremental write)
    # -----------------------------------------------------------------------
    print("Executing Daily Sales aggregation...")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {curated_sales_daily} (
            date string,
            store_id string,
            product_id string,
            total_quantity long,
            total_revenue double,
            order_count long
        ) USING iceberg PARTITIONED BY (date)
    """)

    # Aggregate yesterday's / raw sales daily and insert
    # Group by date, store, product
    spark.sql(f"""
        INSERT INTO {curated_sales_daily}
        SELECT 
            substring(event_time, 1, 10) as date,
            store_id,
            product_id,
            sum(quantity) as total_quantity,
            sum(quantity * price) as total_revenue,
            count(order_id) as order_count
        FROM {raw_orders}
        WHERE status = 'COMPLETED'
        GROUP BY 1, 2, 3
    """)

    # -----------------------------------------------------------------------
    # ETL 2: Inventory By Store (using ACID MERGE INTO upserts)
    # -----------------------------------------------------------------------
    print("Executing Store Inventory MERGE INTO upserts...")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {curated_inventory_store} (
            store_id string,
            product_id string,
            quantity_on_hand int,
            last_updated string,
            supplier_id string
        ) USING iceberg PARTITIONED BY (store_id)
    """)

    # Evolve raw inventory to get latest states per product/store
    spark.sql(f"CREATE OR REPLACE TEMPORARY VIEW latest_inventory_updates AS SELECT * FROM (SELECT store_id, product_id, quantity_on_hand, event_time, supplier_id, row_number() OVER (PARTITION BY store_id, product_id ORDER BY event_time DESC) as rn FROM {raw_inventory}) WHERE rn = 1")

    # Merge updates into curated inventory
    spark.sql(f"""
        MERGE INTO {curated_inventory_store} t
        USING latest_inventory_updates s
        ON t.store_id = s.store_id AND t.product_id = s.product_id
        WHEN MATCHED THEN
            UPDATE SET 
                t.quantity_on_hand = s.quantity_on_hand,
                t.last_updated = s.event_time,
                t.supplier_id = s.supplier_id
        WHEN NOT MATCHED THEN
            INSERT (store_id, product_id, quantity_on_hand, last_updated, supplier_id)
            VALUES (s.store_id, s.product_id, s.quantity_on_hand, s.event_time, s.supplier_id)
    """)

    # -----------------------------------------------------------------------
    # ETL 3: Customer 360 Consolidated Profiles (MERGE signup & tiers)
    # -----------------------------------------------------------------------
    print("Executing Customer 360 consolidation...")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {curated_customer_360} (
            customer_id string,
            first_name string,
            last_name string,
            email string,
            phone string,
            loyalty_tier string,
            last_updated_time string
        ) USING iceberg
    """)

    # Fetch latest customer events
    spark.sql(f"CREATE OR REPLACE TEMPORARY VIEW latest_customer_updates AS SELECT * FROM (SELECT customer_id, first_name, last_name, email, phone, loyalty_tier, event_time, row_number() OVER (PARTITION BY customer_id ORDER BY event_time DESC) as rn FROM {raw_customers}) WHERE rn = 1")

    # Merge updates into customer 360 profiles
    spark.sql(f"""
        MERGE INTO {curated_customer_360} t
        USING latest_customer_updates s
        ON t.customer_id = s.customer_id
        WHEN MATCHED THEN
            UPDATE SET 
                t.first_name = s.first_name,
                t.last_name = s.last_name,
                t.email = s.email,
                t.phone = s.phone,
                t.loyalty_tier = s.loyalty_tier,
                t.last_updated_time = s.event_time
        WHEN NOT MATCHED THEN
            INSERT (customer_id, first_name, last_name, email, phone, loyalty_tier, last_updated_time)
            VALUES (s.customer_id, s.first_name, s.last_name, s.email, s.phone, s.loyalty_tier, s.event_time)
    """)

    # -----------------------------------------------------------------------
    # ETL 4: Product Performance & Pricing (JOIN Daily Sales & Inventory)
    # -----------------------------------------------------------------------
    print("Executing Product Performance profiling...")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {curated_product_perf} (
            product_id string,
            total_units_sold long,
            total_revenue double,
            quantity_in_stock long
        ) USING iceberg
    """)

    spark.sql(f"""
        REPLACE TABLE {curated_product_perf} AS
        SELECT 
            s.product_id,
            sum(s.total_quantity) as total_units_sold,
            sum(s.total_revenue) as total_revenue,
            sum(coalesce(i.quantity_on_hand, 0)) as quantity_in_stock
        FROM {curated_sales_daily} s
        LEFT JOIN {curated_inventory_store} i 
        ON s.product_id = i.product_id AND s.store_id = i.store_id
        GROUP BY s.product_id
    """)

    print("Batch PySpark ETL pipelines executed successfully.")
    spark.stop()

if __name__ == "__main__":
    main()
