# Lab 5: Exploring Apache Iceberg with Dataproc

Lab3 is pre-requisite for Lab5. Please complete Lab3 before starting Lab5.

## In this lab, you will learn how to use **Apache Iceberg** on **Google Cloud Dataproc** to manage large datasets in Cloud Storage with a SQL-like interface. You will create a Dataproc cluster with the necessary Iceberg runtime dependencies, then use PySpark to create an Iceberg table, insert data, and query it.

### Export the following environment variables in your Cloud Shell before starting the lab:
```bash
export PROJECT_ID=<your project id>
export REGION=us-central1
```

### Download the Iceberg Spark runtime JAR and upload it to a GCS bucket for Dataproc to access:
```bash
wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.5.2/iceberg-spark-runtime-3.5_2.12-1.5.2.jar

gcloud storage cp iceberg-spark-runtime-3.5_2.12-1.5.2.jar gs://${PROJECT_ID}-iceberg-warehouse/
```

## Run the following command to create a Dataproc cluster with the Iceberg runtime JAR included in the classpath:

```bash
gcloud dataproc clusters create cluster-lab \
    --region=${REGION} \
    --num-workers=2 \
    --master-machine-type=n2-standard-4 \
    --worker-machine-type=n2-standard-2 \
    --image-version=2.2-debian12 \
    --optional-components=JUPYTER \
    --enable-component-gateway \
--properties="spark:spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,spark:spark.jars=gs://${PROJECT_ID}-iceberg-warehouse/iceberg-spark-runtime-3.5_2.12-1.5.2.jar" \
    --project=${PROJECT_ID}
```

Wait for cluster creation to complete, then open JupyterLab from the cluster's Web Interfaces tab. In JupyterLab, upload`iceberg_notebook.ipynb` to explore creating and querying an Iceberg table on Dataproc!