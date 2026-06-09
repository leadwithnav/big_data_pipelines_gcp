export PROJECT_ID=<your project id>
export REGION=us-central1

Create a Dataproc cluster with the following command. Make sure to replace the region and project ID with your values.

gcloud dataproc clusters create cluster-lab \
    --region=${REGION} \
    --num-workers=2 \
    --master-machine-type=n2-standard-4 \
    --worker-machine-type=n2-standard-2 \
    --image-version=2.2-debian12 \
    --optional-components=JUPYTER \
    --enable-component-gateway \
--properties="spark:spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,spark:spark.jars=gs://upgradlabs-1750853349290-iceberg-warehouse/iceberg-spark-runtime-3.5_2.12-1.5.2.jar" \
    --project=${PROJECT_ID}


