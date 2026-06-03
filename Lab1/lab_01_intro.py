#!/usr/bin/env python
# coding: utf-8

"""
Lab 1: Introduction to Apache Spark (PySpark)
This script demonstrates basic PySpark operations using a movies dataset.
It is designed to be run on a Google Cloud Dataproc cluster or locally.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, avg, desc

def main():
    print("="*50)
    print("Starting Lab 1: Introduction to Apache Spark")
    print("="*50)

    # 1. Initialize SparkSession
    # The SparkSession is the entry point to programming Spark with the Dataset and DataFrame API.
    # In a Dataproc environment, or when submitted via spark-submit, the master is usually configured automatically.
    print("Initializing SparkSession...")
    spark = SparkSession.builder \
        .appName("Lab 1 - Intro to PySpark - Movies") \
        .getOrCreate()

    # To reduce verbosity of logs, you can set log level to WARN or ERROR
    spark.sparkContext.setLogLevel("WARN")

    # 2. Read the CSV Dataset
    # We will read 'movies.csv' which should be present in the same directory, 
    # or passed as an argument/HDFS path in a real Dataproc job.
    file_path = "movies.csv"
    print(f"\nLoading dataset from {file_path}...")
    
    try:
        # Load the CSV file into a DataFrame
        # 'header=True' means the first row contains column names
        # 'inferSchema=True' asks Spark to automatically guess the data types
        df_movies = spark.read.csv(file_path, header=True, inferSchema=True)
    except Exception as e:
        print(f"Error loading file: {e}")
        print("Make sure 'movies.csv' is available in the expected location.")
        spark.stop()
        return

    # 3. Explore the Data (Actions)
    print("\n--- Schema of the DataFrame ---")
    df_movies.printSchema()

    print("\n--- First 5 rows of the DataFrame ---")
    df_movies.show(5, truncate=False)

    print(f"\nTotal number of movies in dataset: {df_movies.count()}")

    # 4. Basic Transformations
    print("\n--- Filter: Movies released after 2000 ---")
    df_modern_movies = df_movies.filter(col("year") >= 2000)
    df_modern_movies.show(5, truncate=False)

    print("\n--- Select & OrderBy: Top 5 Highest Rated Movies ---")
    # Note: the rating column may need to be cast if inferSchema didn't catch it as a double
    # Assuming rating is a double or float
    df_top_rated = df_movies.select("title", "year", "rating") \
                            .orderBy(desc("rating"))
    df_top_rated.show(5, truncate=False)

    # 5. Complex Transformations (Explode & GroupBy)
    # The genres column has multiple genres separated by '|'. Let's split them.
    print("\n--- GroupBy: Average Rating per Genre ---")
    
    # Split the genres string into an array, then explode the array into multiple rows
    df_exploded_genres = df_movies.withColumn("genre", explode(split(col("genres"), r"\|")))
    
    # Group by the new 'genre' column and calculate average rating
    df_genre_ratings = df_exploded_genres.groupBy("genre") \
        .agg(
            avg("rating").alias("avg_rating")
        ) \
        .orderBy(desc("avg_rating"))
        
    df_genre_ratings.show(truncate=False)

    # 6. Writing Data (Action)
    # In a Dataproc environment, this is commonly written back to Cloud Storage (GCS).
    # For this lab, we write out locally or to HDFS.
    output_path = "output1/genre_ratings"
    print(f"\nWriting the result to {output_path} as CSV...")
    try:
        # Repartitioning to 1 so it outputs a single CSV file (for small dataset only)
        df_genre_ratings.repartition(1).write.csv(output_path, header=True, mode="overwrite")
        print("Write successful!")
    except Exception as e:
        print(f"Error writing data: {e}")

    # 7. Stop SparkSession
    print("\nStopping SparkSession...")
    spark.stop()
    print("Lab 1 Completed Successfully!")
    print("="*50)

if __name__ == "__main__":
    main()
