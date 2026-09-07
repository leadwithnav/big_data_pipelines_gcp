import os
import generate_labs

labs_data = [
    # ==================== LAB 0 ====================
    {
        "id": "Lab0",
        "badge": "0",
        "title": "Lab 0: Google Cloud Dataproc and YARN Exploration",
        "modules": [
            {
                "title": "Open Cloud Shell & Set Environment Variables",
                "subtitle": "Activate Cloud Shell, set cluster/region/zone variables, authenticate, and configure your active project.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Dataproc & YARN Overview",
                    "content": "Google Cloud Dataproc is GCP's fully-managed Apache Spark and Hadoop service. YARN (Yet Another Resource Negotiator) acts as the cluster resource manager and job scheduler, allocating memory/CPU containers for Spark applications."
                },
                "explanation": "Before provisioning clusters, auto-detect your project ID, set environment variables (`PROJECT_ID`, `REGION`, `ZONE`, `CLUSTER_NAME`), and authenticate your session.",
                "code_lang": "bash",
                "linux_cmd": "# Auto-detect your active GCP Project ID\nexport PROJECT_ID=$(gcloud config get-value project)\n\n# Choose a region and zone\nexport REGION=us-central1\nexport ZONE=us-central1-a\n\n# Define your cluster name\nexport CLUSTER_NAME=\"cluster-lab\"\n\necho \"Project ID   : $PROJECT_ID\"\necho \"Region       : $REGION\"\necho \"Zone         : $ZONE\"\necho \"Cluster Name : $CLUSTER_NAME\"\n\ngcloud auth login\ngcloud config set project $PROJECT_ID",
                "pwsh_cmd": "# Auto-detect active GCP Project ID in PowerShell\n$env:PROJECT_ID=(gcloud config get-value project)\n\n# Choose a region and zone\n$env:REGION=\"us-central1\"\n$env:ZONE=\"us-central1-a\"\n\n# Define cluster name\n$env:CLUSTER_NAME=\"cluster-lab\"\n\nWrite-Host \"Project ID   : $env:PROJECT_ID\"\nWrite-Host \"Region       : $env:REGION\"\nWrite-Host \"Zone         : $env:ZONE\"\nWrite-Host \"Cluster Name : $env:CLUSTER_NAME\"\n\ngcloud auth login\ngcloud config set project $env:PROJECT_ID",
                "tasks": [
                    {"label": "Set Environment Variables", "desc": "Export PROJECT_ID, REGION, ZONE, and CLUSTER_NAME variables."},
                    {"label": "Authenticate & Set Project", "desc": "Run gcloud auth login and gcloud config set project."}
                ]
            },
            {
                "title": "Create a Dataproc Cluster",
                "subtitle": "Provision a cost-effective single-node Dataproc cluster with Component Gateway enabled.",
                "callout": {
                    "type": "blue",
                    "title": "⚡ Component Gateway",
                    "content": "Enabling `--enable-component-gateway` provides secure web access to YARN ResourceManager, Jupyter, and other Hadoop UIs directly from your browser. Cluster creation typically takes 5 to 7 minutes."
                },
                "explanation": "Run `gcloud dataproc clusters create` using single-node mode with `n2-standard-4` machine type, Debian 12 image version, Jupyter, and Component Gateway enabled.",
                "code_lang": "bash",
                "linux_cmd": "gcloud dataproc clusters create ${CLUSTER_NAME} \\\n    --region=${REGION} \\\n    --zone=${ZONE} \\\n    --single-node \\\n    --master-machine-type=n2-standard-4 \\\n    --image-version=2.2-debian12 \\\n    --enable-component-gateway \\\n    --optional-components=JUPYTER \\\n    --project=${PROJECT_ID}",
                "pwsh_cmd": "gcloud dataproc clusters create $env:CLUSTER_NAME `\n    --region=$env:REGION `\n    --zone=$env:ZONE `\n    --single-node `\n    --master-machine-type=n2-standard-4 `\n    --image-version=2.2-debian12 `\n    --enable-component-gateway `\n    --optional-components=JUPYTER `\n    --project=$env:PROJECT_ID",
                "tasks": [
                    {"label": "Provision Single-Node Cluster", "desc": "Execute gcloud dataproc clusters create command."},
                    {"label": "Verify Cluster Status", "desc": "Confirm cluster state transitions to RUNNING in GCP Console."}
                ]
            },
            {
                "title": "Open the YARN Resource Manager UI",
                "subtitle": "Access the YARN ResourceManager web panel securely via Component Gateway.",
                "callout": {
                    "type": "amber",
                    "title": "🔍 YARN ResourceManager Panel",
                    "content": "The YARN ResourceManager UI displays active node managers, container memory/vCPU allocations, and application execution logs in real-time."
                },
                "explanation": "Navigate to Dataproc → Clusters → click `cluster-lab` → Web Interfaces tab → click YARN ResourceManager. The dashboard will load showing 0 active/completed applications.",
                "code_lang": "bash",
                "linux_cmd": "# Access YARN ResourceManager via Component Gateway in GCP Console:\n# 1. Open https://console.cloud.google.com\n# 2. Go to Dataproc -> Clusters -> cluster-lab\n# 3. Open 'Web Interfaces' tab and click 'YARN ResourceManager'",
                "pwsh_cmd": "# Access YARN ResourceManager via Component Gateway in GCP Console:\n# 1. Open https://console.cloud.google.com\n# 2. Go to Dataproc -> Clusters -> cluster-lab\n# 3. Open 'Web Interfaces' tab and click 'YARN ResourceManager'",
                "tasks": [
                    {"label": "Navigate to Web Interfaces", "desc": "Open cluster-lab details page in Dataproc Console."},
                    {"label": "Launch YARN ResourceManager UI", "desc": "Click YARN ResourceManager link to open monitoring dashboard."}
                ]
            },
            {
                "title": "Submit a Spark Job from Cloud Shell",
                "subtitle": "Submit a pre-packaged Spark Pi calculation job to the cluster.",
                "callout": {
                    "type": "green",
                    "title": "🚀 Job Submission Engine",
                    "content": "Submitting jobs via `gcloud dataproc jobs submit spark` sends the request to the master node, which delegates container allocation and task execution to YARN."
                },
                "explanation": "Run `gcloud dataproc jobs submit spark` referencing the built-in `SparkPi` example JAR located on the cluster master VM to calculate Pi with 1000 iterations.",
                "code_lang": "bash",
                "linux_cmd": "gcloud dataproc jobs submit spark \\\n    --cluster=${CLUSTER_NAME} \\\n    --region=${REGION} \\\n    --project=${PROJECT_ID} \\\n    --class=org.apache.spark.examples.SparkPi \\\n    --jars=file:///usr/lib/spark/examples/jars/spark-examples.jar \\\n    -- 1000",
                "pwsh_cmd": "gcloud dataproc jobs submit spark `\n    --cluster=$env:CLUSTER_NAME `\n    --region=$env:REGION `\n    --project=$env:PROJECT_ID `\n    --class=org.apache.spark.examples.SparkPi `\n    --jars=file:///usr/lib/spark/examples/jars/spark-examples.jar `\n    -- 1000",
                "tasks": [
                    {"label": "Submit SparkPi Job", "desc": "Run gcloud dataproc jobs submit spark command."},
                    {"label": "Observe Execution Logs", "desc": "Monitor job submission STDOUT in Cloud Shell terminal."}
                ]
            },
            {
                "title": "Verify Application on YARN UI & Dataproc Jobs CLI",
                "subtitle": "Trace Spark application lifecycle in YARN UI and inspect job status via gcloud Dataproc CLI.",
                "callout": {
                    "type": "purple",
                    "title": "📊 Job & YARN Application Verification",
                    "content": "Observe the application transition from ACCEPTED → RUNNING → FINISHED in the YARN ResourceManager Web UI (via Component Gateway). You can also list and describe job details directly using `gcloud dataproc jobs` commands without needing SSH permissions."
                },
                "explanation": "Return to your YARN ResourceManager browser tab to verify `org.apache.spark.examples.SparkPi`. Alternatively, run `gcloud dataproc jobs list` and `gcloud dataproc jobs describe` in Cloud Shell to query job status and execution details.",
                "code_lang": "bash",
                "linux_cmd": "# 1. List Dataproc jobs submitted to the cluster\ngcloud dataproc jobs list --region=${REGION}\n\n# 2. Inspect detailed job status and STDOUT/STDERR logs\ngcloud dataproc jobs describe [JOB_ID] --region=${REGION}",
                "pwsh_cmd": "# 1. List Dataproc jobs submitted to the cluster\ngcloud dataproc jobs list --region=$env:REGION\n\n# 2. Inspect detailed job status and STDOUT/STDERR logs\ngcloud dataproc jobs describe [JOB_ID] --region=$env:REGION",
                "tasks": [
                    {"label": "Verify Spark Application State", "desc": "Confirm application state reaches FINISHED in YARN UI."},
                    {"label": "List Dataproc Jobs via CLI", "desc": "Run gcloud dataproc jobs list --region=${REGION}."},
                    {"label": "Describe Job Details", "desc": "Run gcloud dataproc jobs describe [JOB_ID] for logs."}
                ]
            },
            {
                "title": "Cluster Status Verification (Keep Cluster Active)",
                "subtitle": "Maintain your active Dataproc cluster for upcoming hands-on labs.",
                "callout": {
                    "type": "amber",
                    "title": "📌 Cluster Preservation",
                    "content": "Do NOT delete this cluster. The active Dataproc cluster `cluster-lab` will be reused for subsequent training labs."
                },
                "explanation": "Leave the Dataproc cluster running. Run `gcloud dataproc clusters list` to verify that your cluster remains in state RUNNING before moving to Lab 1.",
                "code_lang": "bash",
                "linux_cmd": "# Verify Dataproc cluster remains active for subsequent labs\ngcloud dataproc clusters list --region=${REGION}",
                "pwsh_cmd": "# Verify Dataproc cluster remains active for subsequent labs\ngcloud dataproc clusters list --region=$env:REGION",
                "tasks": [
                    {"label": "Preserve Active Cluster", "desc": "Do NOT delete the Dataproc cluster."},
                    {"label": "Verify RUNNING Status", "desc": "Confirm cluster status is RUNNING using gcloud dataproc clusters list."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What is the primary role of YARN (Yet Another Resource Negotiator) in Google Cloud Dataproc clusters?",
                "options": [
                    {"text": "A) Persistent SQL Database Storage", "correct": False},
                    {"text": "B) Cluster Resource Management and Job Container Scheduling", "correct": True},
                    {"text": "C) Web Browser Rendering Engine", "correct": False},
                    {"text": "D) Object Bucket Synchronization", "correct": False}
                ]
            },
            {
                "question": "Which gcloud flag enables secure browser access to YARN ResourceManager without manual SSH port forwarding?",
                "options": [
                    {"text": "A) --public-ip", "correct": False},
                    {"text": "B) --enable-component-gateway", "correct": True},
                    {"text": "C) --open-ports=8088", "correct": False},
                    {"text": "D) --expose-yarn", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 1 ====================
    {
        "id": "Lab1",
        "badge": "1",
        "title": "Lab 1: Introduction to Apache Spark (PySpark)",
        "modules": [
            {
                "title": "Use Active Dataproc Cluster (`cluster-lab`)",
                "subtitle": "Reuse the active Cloud Dataproc cluster provisioned in Lab 0.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Active Cluster Reuse",
                    "content": "This lab utilizes the active Dataproc cluster `cluster-lab` created in Lab 0. If you have not completed Lab 0, please run Lab 0 first to provision your cluster with Component Gateway and Jupyter enabled."
                },
                "explanation": "Verify that your `cluster-lab` Dataproc cluster is running in the Google Cloud Console.",
                "code_lang": "bash",
                "linux_cmd": "# Check that cluster-lab is running from Lab 0\ngcloud dataproc clusters list --region=us-central1",
                "pwsh_cmd": "# Check that cluster-lab is running from Lab 0\ngcloud dataproc clusters list --region=us-central1",
                "tasks": [
                    {"label": "Verify Active Cluster", "desc": "Run gcloud dataproc clusters list --region=us-central1."},
                    {"label": "Confirm RUNNING State", "desc": "Ensure cluster-lab is in state RUNNING."}
                ]
            },
            {
                "title": "Access JupyterLab & Upload Files",
                "subtitle": "Launch JupyterLab via Component Gateway and upload `movies.csv` and `lab_01_intro.ipynb`.",
                "callout": {
                    "type": "green",
                    "title": "🌐 JupyterLab via Component Gateway",
                    "content": "Component Gateway allows secure single-sign-on access to JupyterLab directly from the GCP Console Web Interfaces tab."
                },
                "explanation": "Navigate to Dataproc → Clusters → click `cluster-lab` → Web Interfaces tab → click **JupyterLab**. In JupyterLab, click the **Upload Files** icon (upward arrow) in the toolbar and upload `movies.csv` and `lab_01_intro.ipynb` from your local Lab1 directory.",
                "code_lang": "bash",
                "linux_cmd": "# 1. Open GCP Console -> Dataproc -> Clusters -> cluster-lab\n# 2. Go to 'Web Interfaces' tab and click 'JupyterLab'\n# 3. In JupyterLab file explorer, click Upload icon (upward arrow)\n# 4. Select and upload movies.csv and lab_01_intro.ipynb",
                "pwsh_cmd": "# 1. Open GCP Console -> Dataproc -> Clusters -> cluster-lab\n# 2. Go to 'Web Interfaces' tab and click 'JupyterLab'\n# 3. In JupyterLab file explorer, click Upload icon (upward arrow)\n# 4. Select and upload movies.csv and lab_01_intro.ipynb",
                "tasks": [
                    {"label": "Open JupyterLab UI", "desc": "Access JupyterLab from Dataproc Web Interfaces tab."},
                    {"label": "Upload Dataset & Notebook", "desc": "Upload movies.csv and lab_01_intro.ipynb into JupyterLab workspace."}
                ]
            },
            {
                "title": "Load `movies.csv` into HDFS",
                "subtitle": "Open JupyterLab Terminal and copy `movies.csv` into HDFS distributed storage.",
                "callout": {
                    "type": "amber",
                    "title": "📁 HDFS Storage",
                    "content": "Hadoop Distributed File System (HDFS) distributes file blocks across cluster node disks for parallel high-throughput reading by Spark executors."
                },
                "explanation": "In JupyterLab Launcher, click **Terminal** to open a bash terminal on the master node, then run `hdfs dfs` commands to stage `movies.csv` in `/data/`.",
                "code_lang": "bash",
                "linux_cmd": "# In JupyterLab Terminal on Master VM:\nhdfs dfs -mkdir -p /data\n\n# Put local movies.csv into HDFS /data directory\nhdfs dfs -put movies.csv /data/\n\n# Verify dataset exists in HDFS\nhdfs dfs -ls /data",
                "pwsh_cmd": "# In JupyterLab Terminal on Master VM:\nhdfs dfs -mkdir -p /data\n\n# Put local movies.csv into HDFS /data directory\nhdfs dfs -put movies.csv /data/\n\n# Verify dataset exists in HDFS\nhdfs dfs -ls /data",
                "tasks": [
                    {"label": "Open JupyterLab Terminal", "desc": "Click Terminal in JupyterLab Launcher interface."},
                    {"label": "Create HDFS Directory", "desc": "Run hdfs dfs -mkdir -p /data."},
                    {"label": "Load File into HDFS", "desc": "Run hdfs dfs -put movies.csv /data/ and verify with hdfs dfs -ls /data."}
                ]
            },
            {
                "title": "Open & Run PySpark Jupyter Notebook (`lab_01_intro.ipynb`)",
                "subtitle": "Execute interactive PySpark DataFrame transformations and aggregations.",
                "callout": {
                    "type": "purple",
                    "title": "⚡ PySpark Transformations & Aggregations",
                    "content": "Spark transformations (`filter`, `withColumn`, `explode`, `groupBy`) build execution plans. Actions (`show`, `write`) execute distributed physical computation."
                },
                "explanation": "In JupyterLab file browser, double-click `lab_01_intro.ipynb`, select **PySpark** kernel, and run notebook cells sequentially.",
                "code_lang": "python",
                "linux_cmd": "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col, desc, explode, split, avg\n\n# 1. Initialize SparkSession\nspark = SparkSession.builder \\\n    .appName(\"Lab 1 - Intro to PySpark - Movies\") \\\n    .getOrCreate()\n\n# 2. Read dataset from HDFS\nfile_path = \"/data/movies.csv\"\ndf_movies = spark.read.csv(file_path, header=True, inferSchema=True)\ndf_movies.printSchema()\ndf_movies.show(5, truncate=False)\n\n# 3. Filter modern movies (released >= 2000)\ndf_modern_movies = df_movies.filter(col(\"year\") >= 2000)\ndf_modern_movies.show(5, truncate=False)\n\n# 4. Explode pipe-delimited genres and compute average rating per genre\ndf_exploded_genres = df_movies.withColumn(\"genre\", explode(split(col(\"genres\"), \"\\\\|\")))\ndf_genre_ratings = df_exploded_genres.groupBy(\"genre\") \\\n    .agg(avg(\"rating\").alias(\"avg_rating\")) \\\n    .orderBy(desc(\"avg_rating\"))\ndf_genre_ratings.show(10, truncate=False)\n\n# 5. Write aggregated result back to HDFS/Storage\ndf_genre_ratings.repartition(1).write.mode(\"overwrite\").csv(\"output/genre_ratings\", header=True)",
                "pwsh_cmd": "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col, desc, explode, split, avg\n\n# 1. Initialize SparkSession\nspark = SparkSession.builder \\\n    .appName(\"Lab 1 - Intro to PySpark - Movies\") \\\n    .getOrCreate()\n\n# 2. Read dataset from HDFS\nfile_path = \"/data/movies.csv\"\ndf_movies = spark.read.csv(file_path, header=True, inferSchema=True)\ndf_movies.printSchema()\ndf_movies.show(5, truncate=False)\n\n# 3. Filter modern movies (released >= 2000)\ndf_modern_movies = df_movies.filter(col(\"year\") >= 2000)\ndf_modern_movies.show(5, truncate=False)\n\n# 4. Explode pipe-delimited genres and compute average rating per genre\ndf_exploded_genres = df_movies.withColumn(\"genre\", explode(split(col(\"genres\"), \"\\\\|\")))\ndf_genre_ratings = df_exploded_genres.groupBy(\"genre\") \\\n    .agg(avg(\"rating\").alias(\"avg_rating\")) \\\n    .orderBy(desc(\"avg_rating\"))\ndf_genre_ratings.show(10, truncate=False)\n\n# 5. Write aggregated result back to HDFS/Storage\ndf_genre_ratings.repartition(1).write.mode(\"overwrite\").csv(\"output/genre_ratings\", header=True)",
                "tasks": [
                    {"label": "Select PySpark Kernel", "desc": "Open lab_01_intro.ipynb and select PySpark kernel."},
                    {"label": "Run SparkSession & Read CSV", "desc": "Execute SparkSession initialization and CSV reader cells."},
                    {"label": "Run Explosive Aggregation", "desc": "Execute explode and groupBy rating aggregation cells."},
                    {"label": "Write Output to Storage", "desc": "Execute df_genre_ratings.write.mode('overwrite').csv cell."}
                ]
            },
            {
                "title": "Verify Output & Preserve Cluster",
                "subtitle": "Inspect generated output files in HDFS and keep cluster active for Lab 1.1.",
                "callout": {
                    "type": "amber",
                    "title": "📌 Cluster Preservation",
                    "content": "Do NOT delete `cluster-lab`. Keep the cluster running as it will be reused for Lab 1.1 (Spark Architecture - Partitions, Jobs, Stages & Tasks)."
                },
                "explanation": "In JupyterLab Terminal, run `hdfs dfs -ls output/genre_ratings` to verify generated CSV partition files.",
                "code_lang": "bash",
                "linux_cmd": "# Check HDFS output directory in JupyterLab Terminal:\nhdfs dfs -ls output/genre_ratings\n\n# Confirm cluster remains running:\ngcloud dataproc clusters list --region=us-central1",
                "pwsh_cmd": "# Check HDFS output directory in JupyterLab Terminal:\nhdfs dfs -ls output/genre_ratings\n\n# Confirm cluster remains running:\ngcloud dataproc clusters list --region=us-central1",
                "tasks": [
                    {"label": "Verify HDFS Output Files", "desc": "Run hdfs dfs -ls output/genre_ratings in Terminal."},
                    {"label": "Preserve Active Cluster", "desc": "Keep cluster-lab in RUNNING state for Lab 1.1."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What fundamental data structure underlies PySpark DataFrames?",
                "options": [
                    {"text": "A) Python Dictionaries", "correct": False},
                    {"text": "B) Resilient Distributed Datasets (RDDs)", "correct": True},
                    {"text": "C) Pandas DataFrames", "correct": False},
                    {"text": "D) MySQL Tables", "correct": False}
                ]
            },
            {
                "question": "Why is Parquet format preferred over CSV for analytical queries in Big Data storage?",
                "options": [
                    {"text": "A) Parquet is plain human-readable text", "correct": False},
                    {"text": "B) Parquet uses columnar storage with compression for significantly faster reads", "correct": True},
                    {"text": "C) CSV files cannot store numbers", "correct": False},
                    {"text": "D) Parquet requires no CPU to process", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 1_1 ====================
    {
        "id": "Lab1_1",
        "badge": "1.1",
        "title": "Lab 1.1: Spark Architecture - Partitions, Jobs, Stages & Tasks",
        "modules": [
            {
                "title": "Prerequisites & Active Dataproc Cluster (`cluster-lab`)",
                "subtitle": "Verify active GCP Project and reuse the active Cloud Dataproc cluster provisioned in Lab 1.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Spark Execution Engine",
                    "content": "Spark breaks application code into Jobs, divides Jobs into Stages based on shuffle boundaries, and executes Tasks across dataset Partitions."
                },
                "explanation": "Verify your Google Cloud Project ID and check that `cluster-lab` is running. If you already have `cluster-lab` active from Lab 1, skip creation.",
                "code_lang": "bash",
                "linux_cmd": "# Set environment variables\nexport PROJECT_ID=$(gcloud config get-value project)\nexport REGION=us-central1\n\n# Verify active cluster-lab Dataproc cluster\ngcloud dataproc clusters list --region=${REGION}",
                "pwsh_cmd": "# Set environment variables in PowerShell\n$env:PROJECT_ID=(gcloud config get-value project)\n$env:REGION=\"us-central1\"\n\n# Verify active cluster-lab Dataproc cluster\ngcloud dataproc clusters list --region=$env:REGION",
                "tasks": [
                    {"label": "Set Project & Region", "desc": "Confirm PROJECT_ID and set REGION to us-central1."},
                    {"label": "Verify Active Cluster", "desc": "Run gcloud dataproc clusters list --region=us-central1 and ensure cluster-lab is RUNNING."}
                ]
            },
            {
                "title": "Access JupyterLab & Upload Files",
                "subtitle": "Launch JupyterLab via Component Gateway and upload `ratings.csv` and `spark_architecture.ipynb`.",
                "callout": {
                    "type": "green",
                    "title": "🌐 JupyterLab via Component Gateway",
                    "content": "Component Gateway allows secure single-sign-on access to JupyterLab directly from the GCP Console Web Interfaces tab without SSH configuration."
                },
                "explanation": "Follow these steps in the Google Cloud Console & JupyterLab UI:\n1. Navigate to Dataproc → Clusters.\n2. Click cluster-lab.\n3. Open the Web Interfaces tab and click JupyterLab.\n4. In the JupyterLab left sidebar, click the Folder icon.\n5. Click the Upload Files button (upward arrow) and upload `ratings.csv` and `spark_architecture.ipynb` from the Lab1_1 folder.",
                "code_lang": "bash",
                "linux_cmd": "# UI Navigation:\n# 1. Open GCP Console -> Dataproc -> Clusters -> cluster-lab\n# 2. Click 'Web Interfaces' tab -> Click 'JupyterLab'\n# 3. Click Folder icon in left sidebar\n# 4. Click 'Upload Files' icon (upward arrow) and upload:\n#    - ratings.csv\n#    - spark_architecture.ipynb",
                "pwsh_cmd": "# UI Navigation:\n# 1. Open GCP Console -> Dataproc -> Clusters -> cluster-lab\n# 2. Click 'Web Interfaces' tab -> Click 'JupyterLab'\n# 3. Click Folder icon in left sidebar\n# 4. Click 'Upload Files' icon (upward arrow) and upload:\n#    - ratings.csv\n#    - spark_architecture.ipynb",
                "tasks": [
                    {"label": "Open JupyterLab UI", "desc": "Access JupyterLab from the Dataproc Web Interfaces tab."},
                    {"label": "Upload Dataset & Notebook", "desc": "Upload ratings.csv and spark_architecture.ipynb into JupyterLab file explorer."}
                ]
            },
            {
                "title": "Load `ratings.csv` into HDFS",
                "subtitle": "Open JupyterLab Terminal and load `ratings.csv` into distributed HDFS storage.",
                "callout": {
                    "type": "amber",
                    "title": "📁 HDFS Storage Setup",
                    "content": "Loading data into HDFS splits the file into blocks across worker nodes, enabling Spark to create distributed partitions for parallel execution."
                },
                "explanation": "In JupyterLab Launcher, open a **Terminal** session and run HDFS CLI commands to create `/data` and put `ratings.csv` into HDFS.",
                "code_lang": "bash",
                "linux_cmd": "# Create a directory in HDFS (skip if /data was created in Lab 1)\nhdfs dfs -mkdir -p /data\n\n# Load ratings.csv from local workspace into HDFS\nhdfs dfs -put ratings.csv /data/\n\n# Verify the file is stored in HDFS\nhdfs dfs -ls /data",
                "pwsh_cmd": "# Create a directory in HDFS (skip if /data was created in Lab 1)\nhdfs dfs -mkdir -p /data\n\n# Load ratings.csv from local workspace into HDFS\nhdfs dfs -put ratings.csv /data/\n\n# Verify the file is stored in HDFS\nhdfs dfs -ls /data",
                "tasks": [
                    {"label": "Open JupyterLab Terminal", "desc": "Click Terminal from the JupyterLab Launcher menu."},
                    {"label": "Create HDFS /data Directory", "desc": "Run hdfs dfs -mkdir -p /data."},
                    {"label": "Stage ratings.csv in HDFS", "desc": "Run hdfs dfs -put ratings.csv /data/ and verify with hdfs dfs -ls /data."}
                ]
            },
            {
                "title": "Open & Run PySpark Jupyter Notebook (`spark_architecture.ipynb`)",
                "subtitle": "Execute PySpark transformations and observe partition behavior and shuffle boundaries.",
                "callout": {
                    "type": "purple",
                    "title": "⚡ PySpark Transformations & Shuffling",
                    "content": "Narrow transformations (filter, map) do not shuffle data across nodes. Wide transformations (groupBy, join) trigger network shuffles across stage boundaries."
                },
                "explanation": "In JupyterLab file browser, double-click `spark_architecture.ipynb`, select **PySpark** kernel, and run cells sequentially to perform Spark transformations and actions.",
                "code_lang": "python",
                "linux_cmd": "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col\n\n# 1. Initialize SparkSession\nspark = SparkSession.builder \\\n    .appName(\"Lab1_1-Spark-Architecture-Exploration\") \\\n    .getOrCreate()\n\n# 2. Read ratings dataset from HDFS\ndf_ratings = spark.read.csv(\"hdfs:///data/ratings.csv\", header=True, inferSchema=True)\nprint(\"Initial Partition Count:\", df_ratings.rdd.getNumPartitions())\n\n# 3. Narrow Transformation (Filter - No Shuffle)\nhigh_ratings = df_ratings.filter(col(\"rating\") >= 4.0)\n\n# 4. Wide Transformation (GroupBy - Triggers Shuffle Stage Boundary)\navg_user_ratings = high_ratings.groupBy(\"userId\").avg(\"rating\")\navg_user_ratings.show(5)",
                "pwsh_cmd": "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col\n\n# 1. Initialize SparkSession\nspark = SparkSession.builder \\\n    .appName(\"Lab1_1-Spark-Architecture-Exploration\") \\\n    .getOrCreate()\n\n# 2. Read ratings dataset from HDFS\ndf_ratings = spark.read.csv(\"hdfs:///data/ratings.csv\", header=True, inferSchema=True)\nprint(\"Initial Partition Count:\", df_ratings.rdd.getNumPartitions())\n\n# 3. Narrow Transformation (Filter - No Shuffle)\nhigh_ratings = df_ratings.filter(col(\"rating\") >= 4.0)\n\n# 4. Wide Transformation (GroupBy - Triggers Shuffle Stage Boundary)\navg_user_ratings = high_ratings.groupBy(\"userId\").avg(\"rating\")\navg_user_ratings.show(5)",
                "tasks": [
                    {"label": "Select PySpark Kernel", "desc": "Double-click spark_architecture.ipynb and select PySpark kernel."},
                    {"label": "Run Notebook Cells", "desc": "Execute cells sequentially to calculate partitions and user average ratings."},
                    {"label": "Observe Transformations", "desc": "Distinguish narrow filter operations from wide groupBy shuffle operations."}
                ]
            },
            {
                "title": "Explore Jobs, Stages & Tasks in Spark UI",
                "subtitle": "Inspect the Spark Application UI / History Server to analyze DAG execution details.",
                "callout": {
                    "type": "blue",
                    "title": "🌐 Spark Application UI & DAG Inspector",
                    "content": "The DAG Scheduler visualizes Jobs, Stages, Shuffle read/write metrics, and parallel Tasks per partition."
                },
                "explanation": "Navigate to Google Cloud Console → Dataproc → Clusters → `cluster-lab` → Web Interfaces tab → click Spark History Server or Spark Application UI:\n1. Locate your session `Lab1_1-Spark-Architecture-Exploration`.\n2. **Jobs Tab**: Each action (`.count()`, `.show()`) triggers a separate Job.\n3. **Stages Tab**: Filter ran in 1 Stage (no shuffle); GroupBy ran in 2 Stages (shuffle boundary).\n4. **Tasks Detail**: Task count matches partition count.",
                "code_lang": "bash",
                "linux_cmd": "# Web UI Access:\n# 1. Open GCP Console -> Dataproc -> Clusters -> cluster-lab\n# 2. Click 'Web Interfaces' tab -> Click 'Spark History Server' or 'Spark UI'\n# 3. Open application 'Lab1_1-Spark-Architecture-Exploration'\n# 4. Inspect Jobs, Stages (DAG Visualization), and Tasks detail",
                "pwsh_cmd": "# Web UI Access:\n# 1. Open GCP Console -> Dataproc -> Clusters -> cluster-lab\n# 2. Click 'Web Interfaces' tab -> Click 'Spark History Server' or 'Spark UI'\n# 3. Open application 'Lab1_1-Spark-Architecture-Exploration'\n# 4. Inspect Jobs, Stages (DAG Visualization), and Tasks detail",
                "tasks": [
                    {"label": "Access Spark UI", "desc": "Open Spark History Server / Spark Application UI via Component Gateway."},
                    {"label": "Inspect Jobs & Actions", "desc": "Verify that each action in the notebook created a separate Job."},
                    {"label": "Analyze Stages & DAG", "desc": "Check shuffle boundaries (Filter = 1 Stage, GroupBy = 2 Stages)."},
                    {"label": "Verify Task Count", "desc": "Confirm that Task count per Stage matches dataset partition count."}
                ]
            },
            {
                "title": "Cluster Management & Optional Cleanup",
                "subtitle": "Optionally delete the cluster when finished or retain it for future labs.",
                "callout": {
                    "type": "amber",
                    "title": "⚠️ Cluster Lifecycle",
                    "content": "Delete your cluster when finished with all labs to avoid compute charges, or keep it running if continuing with subsequent labs."
                },
                "explanation": "Run `gcloud dataproc clusters delete` if you wish to tear down cluster resources when completed.",
                "code_lang": "bash",
                "linux_cmd": "# Optional: Delete cluster-lab when finished with all labs\ngcloud dataproc clusters delete cluster-lab --region=us-central1 --quiet",
                "pwsh_cmd": "# Optional: Delete cluster-lab when finished with all labs\ngcloud dataproc clusters delete cluster-lab --region=us-central1 --quiet",
                "tasks": [
                    {"label": "Verify Resource State", "desc": "Check running resources in your GCP project."},
                    {"label": "Optional Cleanup", "desc": "Run gcloud dataproc clusters delete cluster-lab when ready to tear down."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What separates a Wide Transformation from a Narrow Transformation in Apache Spark?",
                "options": [
                    {"text": "A) Narrow transformations can only be run on master nodes", "correct": False},
                    {"text": "B) Wide transformations require data shuffling across cluster nodes, creating new stage boundaries", "correct": True},
                    {"text": "C) Narrow transformations process strings while wide transformations process numbers", "correct": False},
                    {"text": "D) Wide transformations execute instantly without lazy evaluation", "correct": False}
                ]
            },
            {
                "question": "Which method is recommended when decreasing partition count after filtering data to avoid unnecessary network shuffles?",
                "options": [
                    {"text": "A) repartition()", "correct": False},
                    {"text": "B) coalesce()", "correct": True},
                    {"text": "C) rdd.glom()", "correct": False},
                    {"text": "D) spark.read.option('partitions', 1)", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 2 ====================
    {
        "id": "Lab2",
        "badge": "2",
        "title": "Lab 2: Google Cloud Pub/Sub Publisher & Subscriber",
        "modules": [
            {
                "title": "Set Environment Variables",
                "subtitle": "Export PROJECT_ID in Cloud Shell.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Google Cloud Pub/Sub",
                    "content": "Google Cloud Pub/Sub is an asynchronous, serverless messaging service that decouples event-producing publishers from event-processing subscribers."
                },
                "explanation": "Activate Cloud Shell and set your active GCP Project ID.",
                "code_lang": "bash",
                "linux_cmd": "# Auto-detect your active GCP Project ID\nexport PROJECT_ID=$(gcloud config get-value project)\necho \"Project ID : $PROJECT_ID\"",
                "pwsh_cmd": "# Set active GCP Project ID in PowerShell\n$env:PROJECT_ID=(gcloud config get-value project)\nWrite-Host \"Project ID : $env:PROJECT_ID\"",
                "tasks": [
                    {"label": "Set PROJECT_ID Variable", "desc": "Confirm PROJECT_ID environment variable is set using gcloud config get-value project."}
                ]
            },
            {
                "title": "Create Pub/Sub Topic (`lab2-topic`) & Subscription (`lab2-sub`)",
                "subtitle": "Provision the Pub/Sub topic and pull subscription using gcloud CLI.",
                "callout": {
                    "type": "blue",
                    "title": "📢 Topics & Subscriptions",
                    "content": "Publishers send messages to a Topic (`lab2-topic`). Subscriptions (`lab2-sub`) pull or stream messages published to that topic."
                },
                "explanation": "Run `gcloud pubsub` commands to create topic `lab2-topic` and subscription `lab2-sub`.",
                "code_lang": "bash",
                "linux_cmd": "# Create the Pub/Sub Topic\ngcloud pubsub topics create lab2-topic --project=${PROJECT_ID}\n\n# Create a pull subscription bound to the topic\ngcloud pubsub subscriptions create lab2-sub --topic=lab2-topic --project=${PROJECT_ID}",
                "pwsh_cmd": "# Create the Pub/Sub Topic\ngcloud pubsub topics create lab2-topic --project=$env:PROJECT_ID\n\n# Create a pull subscription bound to the topic\ngcloud pubsub subscriptions create lab2-sub --topic=lab2-topic --project=$env:PROJECT_ID",
                "tasks": [
                    {"label": "Create Topic", "desc": "Run gcloud pubsub topics create lab2-topic."},
                    {"label": "Create Subscription", "desc": "Run gcloud pubsub subscriptions create lab2-sub --topic=lab2-topic."}
                ]
            },
            {
                "title": "Install Python Dependencies (`requirements.txt`)",
                "subtitle": "Navigate to Lab2 workspace directory and install required Google Cloud Pub/Sub client library.",
                "callout": {
                    "type": "green",
                    "title": "📦 Python Pub/Sub Client",
                    "content": "The `google-cloud-pubsub` Python library provides high-performance asynchronous publishers and streaming pull subscribers."
                },
                "explanation": "Navigate to the Lab2 folder and install dependencies listed in `requirements.txt`.",
                "code_lang": "bash",
                "linux_cmd": "# Navigate to the Lab 2 directory\ncd ~/big_data_pipelines_gcp/Lab2\n\n# Install required packages\npip install -r requirements.txt",
                "pwsh_cmd": "# Navigate to the Lab 2 directory\ncd D:\\trainings\\GCP_Big_Data_Pipelines\\Lab2\n\n# Install required packages\npip install -r requirements.txt",
                "tasks": [
                    {"label": "Navigate to Lab2 Directory", "desc": "Change directory to the Lab2 folder."},
                    {"label": "Install Dependencies", "desc": "Run pip install -r requirements.txt."}
                ]
            },
            {
                "title": "Run the Telemetry Publisher (`publisher.py`)",
                "subtitle": "Publish IoT sensor records from `sensor_data.csv` continuously to `lab2-topic`.",
                "callout": {
                    "type": "purple",
                    "title": "📤 Telemetry Streaming Publisher",
                    "content": "`publisher.py` reads `sensor_data.csv`, injects current UTC timestamps, and continuously streams JSON payload records to `lab2-topic`."
                },
                "explanation": "Execute `publisher.py` in your primary Cloud Shell terminal tab and keep it running.",
                "code_lang": "bash",
                "linux_cmd": "# Run Telemetry Publisher (keep terminal tab open)\npython publisher.py --project=${PROJECT_ID}",
                "pwsh_cmd": "# Run Telemetry Publisher (keep terminal tab open)\npython publisher.py --project=$env:PROJECT_ID",
                "tasks": [
                    {"label": "Launch Publisher", "desc": "Run python publisher.py --project=${PROJECT_ID}."},
                    {"label": "Verify Output Logs", "desc": "Confirm Published message ID logs are displayed in terminal."}
                ]
            },
            {
                "title": "Run the Telemetry Subscriber (`subscriber.py`)",
                "subtitle": "Open a second terminal tab and run `subscriber.py` to consume and acknowledge messages in real-time.",
                "callout": {
                    "type": "amber",
                    "title": "📥 Message Pull & Acknowledgment",
                    "content": "`subscriber.py` listens to `lab2-sub`, processes incoming telemetry payloads in real-time, and sends message acknowledgments (`ack`) back to Pub/Sub."
                },
                "explanation": "Open a **new Cloud Shell terminal tab**, navigate to Lab2, set `PROJECT_ID`, and run `subscriber.py`.",
                "code_lang": "bash",
                "linux_cmd": "# In a NEW Cloud Shell terminal tab:\ncd ~/big_data_pipelines_gcp/Lab2\nexport PROJECT_ID=$(gcloud config get-value project)\n\n# Run Telemetry Subscriber\npython subscriber.py --project=${PROJECT_ID}",
                "pwsh_cmd": "# In a NEW PowerShell terminal tab:\ncd D:\\trainings\\GCP_Big_Data_Pipelines\\Lab2\n$env:PROJECT_ID=(gcloud config get-value project)\n\n# Run Telemetry Subscriber\npython subscriber.py --project=$env:PROJECT_ID",
                "tasks": [
                    {"label": "Open Second Terminal Tab", "desc": "Launch a second terminal session."},
                    {"label": "Launch Subscriber", "desc": "Run python subscriber.py --project=${PROJECT_ID}."},
                    {"label": "Verify Received Payload", "desc": "Confirm Received message ID logs and message acknowledgments in terminal."}
                ]
            },
            {
                "title": "End-to-End Verification & Cleanup",
                "subtitle": "Stop publisher and subscriber scripts and delete Pub/Sub topic and subscription.",
                "callout": {
                    "type": "red",
                    "title": "🧹 Resource Cleanup",
                    "content": "Stop active streaming background scripts with Ctrl+C and delete topic/subscription resources to avoid unexpected GCP charges."
                },
                "explanation": "Press `Ctrl+C` in both terminal tabs to stop scripts, then delete `lab2-sub` and `lab2-topic`.",
                "code_lang": "bash",
                "linux_cmd": "# 1. Press Ctrl+C in Tab 1 (publisher.py) and Tab 2 (subscriber.py) to stop\n\n# 2. Delete Pub/Sub resources in terminal:\ngcloud pubsub subscriptions delete lab2-sub --project=${PROJECT_ID}\ngcloud pubsub topics delete lab2-topic --project=${PROJECT_ID}",
                "pwsh_cmd": "# 1. Press Ctrl+C in Tab 1 (publisher.py) and Tab 2 (subscriber.py) to stop\n\n# 2. Delete Pub/Sub resources in terminal:\ngcloud pubsub subscriptions delete lab2-sub --project=$env:PROJECT_ID\ngcloud pubsub topics delete lab2-topic --project=$env:PROJECT_ID",
                "tasks": [
                    {"label": "Stop Scripts", "desc": "Press Ctrl+C in both terminal windows."},
                    {"label": "Delete Pub/Sub Resources", "desc": "Delete subscription lab2-sub and topic lab2-topic."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What method must a GCP Pub/Sub subscriber invoke to confirm a message was successfully processed?",
                "options": [
                    {"text": "A) message.delete()", "correct": False},
                    {"text": "B) message.ack()", "correct": True},
                    {"text": "C) message.confirm()", "correct": False},
                    {"text": "D) message.close()", "correct": False}
                ]
            },
            {
                "question": "What occurs when a subscriber fails to acknowledge a message before its ack deadline expires?",
                "options": [
                    {"text": "A) Message is lost permanently", "correct": False},
                    {"text": "B) Message is redelivered to active subscribers", "correct": True},
                    {"text": "C) Topic is automatically deleted", "correct": False},
                    {"text": "D) Publisher throws a fatal error", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 3 ====================
    {
        "id": "Lab3",
        "badge": "3",
        "title": "Lab 3: Apache Beam Streaming Pipeline on Cloud Dataflow",
        "modules": [
            {
                "title": "Environment & API Setup",
                "subtitle": "Enable Dataflow and Compute Engine APIs and set up GCS staging bucket.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Google Cloud Dataflow",
                    "content": "Dataflow is a fully managed, serverless unified stream and batch processing service powered by Apache Beam."
                },
                "explanation": "Enable APIs and provision a staging GCS bucket for Apache Beam pipeline artifacts.",
                "code_lang": "bash",
                "linux_cmd": "gcloud services enable dataflow.googleapis.com compute.googleapis.com pubsub.googleapis.com\ngsutil mb -l us-central1 gs://[YOUR_PROJECT_ID]-dataflow-staging",
                "pwsh_cmd": "gcloud services enable dataflow.googleapis.com compute.googleapis.com pubsub.googleapis.com\ngsutil mb -l us-central1 gs://[YOUR_PROJECT_ID]-dataflow-staging",
                "tasks": [
                    {"label": "Enable GCP APIs", "desc": "Confirm Dataflow and Pub/Sub APIs are enabled."},
                    {"label": "Create Staging GCS Bucket", "desc": "Create Cloud Storage bucket for Dataflow temp binaries."}
                ]
            },
            {
                "title": "Pub/Sub Infrastructure Setup",
                "subtitle": "Create Pub/Sub topic and subscription for streaming ingestion.",
                "callout": {
                    "type": "blue",
                    "title": "📡 Streaming Source",
                    "content": "Dataflow pipelines connect to Pub/Sub topics as real-time unbounded streaming sources."
                },
                "explanation": "Create topic `dataflow-sensor-topic` and subscription `dataflow-sensor-sub`.",
                "code_lang": "bash",
                "linux_cmd": "gcloud pubsub topics create dataflow-sensor-topic\ngcloud pubsub subscriptions create dataflow-sensor-sub --topic=dataflow-sensor-topic",
                "pwsh_cmd": "gcloud pubsub topics create dataflow-sensor-topic\ngcloud pubsub subscriptions create dataflow-sensor-sub --topic=dataflow-sensor-topic",
                "tasks": [
                    {"label": "Create Topic", "desc": "Provision dataflow-sensor-topic."},
                    {"label": "Create Subscription", "desc": "Provision dataflow-sensor-sub."}
                ]
            },
            {
                "title": "Developing Apache Beam Code (`lab_03_dataflow.py`)",
                "subtitle": "Write Apache Beam pipeline code with custom DoFn transforms.",
                "callout": {
                    "type": "green",
                    "title": "🧱 Apache Beam PTransforms & DoFn",
                    "content": "Beam pipelines transform `PCollection` data using parallel `ParDo` operations with custom `DoFn` classes."
                },
                "explanation": "Review Beam pipeline code filtering high-temperature sensor readings from Pub/Sub stream.",
                "code_lang": "python",
                "linux_cmd": "# lab_03_dataflow.py snippet\nimport apache_beam as beam\nfrom apache_beam.options.pipeline_options import PipelineOptions\nimport json\n\nclass FilterHighTempFn(beam.DoFn):\n    def process(self, element):\n        record = json.loads(element.decode('utf-8'))\n        if float(record.get('temperature', 0)) > 80.0:\n            yield record\n\ndef run():\n    options = PipelineOptions(streaming=True, save_main_session=True)\n    with beam.Pipeline(options=options) as p:\n        (p | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription='projects/[PROJECT]/subscriptions/dataflow-sensor-sub')\n           | 'FilterHighTemp' >> beam.ParDo(FilterHighTempFn())\n           | 'LogOutput' >> beam.Map(print))",
                "pwsh_cmd": "# lab_03_dataflow.py snippet\nimport apache_beam as beam\nfrom apache_beam.options.pipeline_options import PipelineOptions\nimport json\n\nclass FilterHighTempFn(beam.DoFn):\n    def process(self, element):\n        record = json.loads(element.decode('utf-8'))\n        if float(record.get('temperature', 0)) > 80.0:\n            yield record\n\ndef run():\n    options = PipelineOptions(streaming=True, save_main_session=True)\n    with beam.Pipeline(options=options) as p:\n        (p | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription='projects/[PROJECT]/subscriptions/dataflow-sensor-sub')\n           | 'FilterHighTemp' >> beam.ParDo(FilterHighTempFn())\n           | 'LogOutput' >> beam.Map(print))",
                "tasks": [
                    {"label": "Verify DoFn Logic", "desc": "Check FilterHighTempFn parsing and yield threshold."},
                    {"label": "Configure PipelineOptions", "desc": "Set streaming=True in PipelineOptions."}
                ]
            },
            {
                "title": "Local Execution (DirectRunner) vs Cloud (DataflowRunner)",
                "subtitle": "Test locally with DirectRunner, then submit job to Cloud Dataflow.",
                "callout": {
                    "type": "amber",
                    "title": "🚀 DataflowRunner Deployment",
                    "content": "DataflowRunner automatically provisions worker VMs, auto-scales resources, and handles fault tolerance."
                },
                "explanation": "Deploy the streaming pipeline to GCP Dataflow using `DataflowRunner`.",
                "code_lang": "bash",
                "linux_cmd": "# Test locally\npython lab_03_dataflow.py --runner=DirectRunner\n\n# Deploy to Cloud Dataflow\npython lab_03_dataflow.py \\\n  --runner=DataflowRunner \\\n  --project=[YOUR_PROJECT_ID] \\\n  --region=us-central1 \\\n  --temp_location=gs://[YOUR_PROJECT_ID]-dataflow-staging/temp \\\n  --job_name=lab03-streaming-sensor",
                "pwsh_cmd": "# Test locally\npython lab_03_dataflow.py --runner=DirectRunner\n\n# Deploy to Cloud Dataflow\npython lab_03_dataflow.py `\n  --runner=DataflowRunner `\n  --project=[YOUR_PROJECT_ID] `\n  --region=us-central1 `\n  --temp_location=gs://[YOUR_PROJECT_ID]-dataflow-staging/temp `\n  --job_name=lab03-streaming-sensor",
                "tasks": [
                    {"label": "Test DirectRunner", "desc": "Run local DirectRunner execution."},
                    {"label": "Submit Dataflow Job", "desc": "Deploy streaming job with DataflowRunner."}
                ]
            },
            {
                "title": "Monitoring Job & Teardown",
                "subtitle": "Inspect job graph and watermarks in Dataflow UI, then drain/cancel the job.",
                "callout": {
                    "type": "red",
                    "title": "⏹️ Job Cancellation",
                    "content": "Streaming Dataflow jobs run indefinitely until explicitly cancelled or drained."
                },
                "explanation": "Open GCP Dataflow Console, view execution graph, and cancel the active streaming job.",
                "code_lang": "bash",
                "linux_cmd": "gcloud dataflow jobs list --region=us-central1\ngcloud dataflow jobs cancel [JOB_ID] --region=us-central1",
                "pwsh_cmd": "gcloud dataflow jobs list --region=us-central1\ngcloud dataflow jobs cancel [JOB_ID] --region=us-central1",
                "tasks": [
                    {"label": "Monitor Dataflow Graph", "desc": "Inspect System Lag and Data Watermarks in Dataflow UI."},
                    {"label": "Cancel Dataflow Job", "desc": "Run gcloud dataflow jobs cancel command."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "Which Apache Beam runner allows developers to test pipeline code locally before deploying to GCP?",
                "options": [
                    {"text": "A) DataflowRunner", "correct": False},
                    {"text": "B) DirectRunner", "correct": True},
                    {"text": "C) SparkRunner", "correct": False},
                    {"text": "D) FlinkRunner", "correct": False}
                ]
            },
            {
                "question": "What class is subclassed in Apache Beam Python to define custom element-by-element transformations?",
                "options": [
                    {"text": "A) beam.DoFn", "correct": True},
                    {"text": "B) beam.TransformFn", "correct": False},
                    {"text": "C) beam.MapFn", "correct": False},
                    {"text": "D) beam.FilterFn", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 4 ====================
    {
        "id": "Lab4",
        "badge": "4",
        "title": "Lab 4: Apache Beam Windowing and Aggregation on Dataflow",
        "modules": [
            {
                "title": "Infrastructure Setup",
                "subtitle": "Create Cloud Storage staging bucket and Pub/Sub topic for windowed telemetry.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Windowed Stream Processing",
                    "content": "Windowing subdivides unbounded streaming data into finite temporal buckets based on event timestamps."
                },
                "explanation": "Provision GCS staging storage and Pub/Sub topic `windowed-sensor-topic`.",
                "code_lang": "bash",
                "linux_cmd": "gcloud pubsub topics create windowed-sensor-topic\ngcloud pubsub subscriptions create windowed-sensor-sub --topic=windowed-sensor-topic\ngsutil mb -l us-central1 gs://[YOUR_PROJECT_ID]-windowed-staging",
                "pwsh_cmd": "gcloud pubsub topics create windowed-sensor-topic\ngcloud pubsub subscriptions create windowed-sensor-sub --topic=windowed-sensor-topic\ngsutil mb -l us-central1 gs://[YOUR_PROJECT_ID]-windowed-staging",
                "tasks": [
                    {"label": "Create Pub/Sub Topic", "desc": "Create windowed-sensor-topic."},
                    {"label": "Create Staging Bucket", "desc": "Create gs://[PROJECT_ID]-windowed-staging."}
                ]
            },
            {
                "title": "Windowing Concepts & Window Strategies",
                "subtitle": "Understand Fixed Windows, Sliding Windows, and Session Windows.",
                "callout": {
                    "type": "blue",
                    "title": "⏱️ Window Types",
                    "content": "Fixed Windows represent non-overlapping uniform intervals. Sliding Windows overlap with fixed periods. Session Windows group events separated by inactivity gaps."
                },
                "explanation": "Choose the appropriate windowing strategy for aggregating telemetry streams over time.",
                "code_lang": "python",
                "linux_cmd": "# Windowing strategies in Apache Beam\nfrom apache_beam import window\n\n# 60-Second Fixed Windows (Tumbling)\nfixed_windows = window.FixedWindows(60)\n\n# 60-Second Sliding Windows every 30 seconds\nsliding_windows = window.SlidingWindows(size=60, period=30)",
                "pwsh_cmd": "# Windowing strategies in Apache Beam\nfrom apache_beam import window\n\n# 60-Second Fixed Windows (Tumbling)\nfixed_windows = window.FixedWindows(60)\n\n# 60-Second Sliding Windows every 30 seconds\nsliding_windows = window.SlidingWindows(size=60, period=30)",
                "tasks": [
                    {"label": "Review Fixed Windows", "desc": "Understand 60-second tumbling window boundaries."},
                    {"label": "Review Sliding Windows", "desc": "Understand overlapping sliding window periods."}
                ]
            },
            {
                "title": "Implementing Windowed Aggregations (`lab_04_windowed_beam.py`)",
                "subtitle": "Apply `WindowInto` and `CombinePerKey` aggregations in Beam.",
                "callout": {
                    "type": "green",
                    "title": "📊 CombinePerKey Aggregations",
                    "content": "`CombinePerKey` computes parallel summary statistics (e.g. mean, max) for key-value pairs within each window pane."
                },
                "explanation": "Implement windowed average temperature aggregation per device ID in PyBeam.",
                "code_lang": "python",
                "linux_cmd": "# lab_04_windowed_beam.py snippet\nimport apache_beam as beam\nfrom apache_beam.transforms import window\n\nwith beam.Pipeline(options=options) as p:\n    (p | 'Read' >> beam.io.ReadFromPubSub(subscription=sub_path)\n       | 'Parse' >> beam.ParDo(ParseTelemetryFn())\n       | 'Window' >> beam.WindowInto(window.FixedWindows(60))\n       | 'KV' >> beam.Map(lambda x: (x['device_id'], float(x['temperature'])))\n       | 'AvgTemp' >> beam.CombinePerKey(beam.combiners.MeanCombineFn())\n       | 'Format' >> beam.Map(lambda kv: f'Device: {kv[0]} | AvgTemp: {kv[1]:.2f}')\n       | 'Log' >> beam.Map(print))",
                "pwsh_cmd": "# lab_04_windowed_beam.py snippet\nimport apache_beam as beam\nfrom apache_beam.transforms import window\n\nwith beam.Pipeline(options=options) as p:\n    (p | 'Read' >> beam.io.ReadFromPubSub(subscription=sub_path)\n       | 'Parse' >> beam.ParDo(ParseTelemetryFn())\n       | 'Window' >> beam.WindowInto(window.FixedWindows(60))\n       | 'KV' >> beam.Map(lambda x: (x['device_id'], float(x['temperature'])))\n       | 'AvgTemp' >> beam.CombinePerKey(beam.combiners.MeanCombineFn())\n       | 'Format' >> beam.Map(lambda kv: f'Device: {kv[0]} | AvgTemp: {kv[1]:.2f}')\n       | 'Log' >> beam.Map(print))",
                "tasks": [
                    {"label": "Apply WindowInto", "desc": "Add FixedWindows(60) transformation."},
                    {"label": "Apply CombinePerKey", "desc": "Compute MeanCombineFn per device ID."}
                ]
            },
            {
                "title": "Handling Late Data & Allowed Lateness",
                "subtitle": "Configure Watermark triggers and allowed lateness parameters.",
                "callout": {
                    "type": "amber",
                    "title": "💧 Watermarks & Late Data",
                    "content": "Watermarks track event-time arrival progress. `allowed_lateness` permits late-arriving events to re-trigger window calculations."
                },
                "explanation": "Configure trigger spec with `AfterWatermark()` and `allowed_lateness=Duration(seconds=120)`.",
                "code_lang": "python",
                "linux_cmd": "from apache_beam.transforms.trigger import AfterWatermark, AccumulationMode\nfrom apache_beam.utils.timestamp import Duration\n\nwindowed_pcoll = raw_pcoll | beam.WindowInto(\n    window.FixedWindows(60),\n    trigger=AfterWatermark(),\n    allowed_lateness=Duration(seconds=120),\n    accumulation_mode=AccumulationMode.ACCUMULATING\n)",
                "pwsh_cmd": "from apache_beam.transforms.trigger import AfterWatermark, AccumulationMode\nfrom apache_beam.utils.timestamp import Duration\n\nwindowed_pcoll = raw_pcoll | beam.WindowInto(\n    window.FixedWindows(60),\n    trigger=AfterWatermark(),\n    allowed_lateness=Duration(seconds=120),\n    accumulation_mode=AccumulationMode.ACCUMULATING\n)",
                "tasks": [
                    {"label": "Configure AfterWatermark", "desc": "Set AfterWatermark trigger on FixedWindows."},
                    {"label": "Set Allowed Lateness", "desc": "Specify allowed_lateness duration of 120 seconds."}
                ]
            },
            {
                "title": "Deployment & Teardown",
                "subtitle": "Deploy windowed job to Cloud Dataflow and clean up environment.",
                "callout": {
                    "type": "red",
                    "title": "🧹 Teardown",
                    "content": "Cancel Dataflow job and delete Pub/Sub topics upon completion."
                },
                "explanation": "Submit job via `DataflowRunner` and cancel after testing.",
                "code_lang": "bash",
                "linux_cmd": "python lab_04_windowed_beam.py \\\n  --runner=DataflowRunner \\\n  --project=[YOUR_PROJECT_ID] \\\n  --region=us-central1 \\\n  --temp_location=gs://[YOUR_PROJECT_ID]-windowed-staging/temp \\\n  --job_name=lab04-windowed-beam",
                "pwsh_cmd": "python lab_04_windowed_beam.py `\n  --runner=DataflowRunner `\n  --project=[YOUR_PROJECT_ID] `\n  --region=us-central1 `\n  --temp_location=gs://[YOUR_PROJECT_ID]-windowed-staging/temp `\n  --job_name=lab04-windowed-beam",
                "tasks": [
                    {"label": "Deploy Dataflow Job", "desc": "Run pipeline with DataflowRunner."},
                    {"label": "Cancel Job", "desc": "Cancel streaming job in Dataflow UI."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What type of window divides a stream into consistent, non-overlapping time buckets?",
                "options": [
                    {"text": "A) Sliding Windows", "correct": False},
                    {"text": "B) Fixed Windows (Tumbling Windows)", "correct": True},
                    {"text": "C) Session Windows", "correct": False},
                    {"text": "D) Global Windows", "correct": False}
                ]
            },
            {
                "question": "What does the Watermark estimate in event-time stream processing?",
                "options": [
                    {"text": "A) Total memory consumed by worker VMs", "correct": False},
                    {"text": "B) Progress estimate that all data up to a given event-time timestamp has arrived", "correct": True},
                    {"text": "C) Network bandwidth latency", "correct": False},
                    {"text": "D) Number of unread GCS objects", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 5 ====================
    {
        "id": "Lab5",
        "badge": "5",
        "title": "Lab 5: Exploring Apache Iceberg with Dataproc",
        "modules": [
            {
                "title": "Dataproc Provisioning with Apache Iceberg",
                "subtitle": "Provision Dataproc cluster pre-configured with Apache Iceberg Spark connector.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Apache Iceberg",
                    "content": "Apache Iceberg is an open table format for massive analytic datasets, bringing ACID transactions, snapshot isolation, and time travel to data lakes on GCS."
                },
                "explanation": "Create Dataproc cluster configured with Iceberg Spark runtime packages.",
                "code_lang": "bash",
                "linux_cmd": "gcloud dataproc clusters create iceberg-lab5-cluster \\\n  --region=us-central1 \\\n  --single-node \\\n  --optional-components=JUPYTER \\\n  --enable-component-gateway \\\n  --properties=spark:spark.jars.packages=org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0",
                "pwsh_cmd": "gcloud dataproc clusters create iceberg-lab5-cluster `\n  --region=us-central1 `\n  --optional-components=JUPYTER `\n  --enable-component-gateway `\n  --properties=spark:spark.jars.packages=org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0",
                "tasks": [
                    {"label": "Create Iceberg Cluster", "desc": "Provision Dataproc cluster with Iceberg Spark runtime JAR."},
                    {"label": "Launch JupyterLab", "desc": "Access JupyterLab from Component Gateway."}
                ]
            },
            {
                "title": "Configuring Spark Iceberg Catalog",
                "subtitle": "Configure SparkSession catalog properties pointing to GCS warehouse.",
                "callout": {
                    "type": "blue",
                    "title": "🗃️ Iceberg Catalog",
                    "content": "Iceberg catalogs track table state pointer updates atomically. A Hadoop catalog uses filesystem paths in GCS."
                },
                "explanation": "Initialize SparkSession with `spark.sql.catalog.iceberg` catalog configuration.",
                "code_lang": "python",
                "linux_cmd": "from pyspark.sql import SparkSession\n\nspark = SparkSession.builder \\\n    .appName('Iceberg-Lab5') \\\n    .config('spark.sql.catalog.iceberg', 'org.apache.iceberg.spark.SparkCatalog') \\\n    .config('spark.sql.catalog.iceberg.type', 'hadoop') \\\n    .config('spark.sql.catalog.iceberg.warehouse', 'gs://[YOUR_BUCKET_NAME]/iceberg-warehouse') \\\n    .getOrCreate()",
                "pwsh_cmd": "from pyspark.sql import SparkSession\n\nspark = SparkSession.builder \\\n    .appName('Iceberg-Lab5') \\\n    .config('spark.sql.catalog.iceberg', 'org.apache.iceberg.spark.SparkCatalog') \\\n    .config('spark.sql.catalog.iceberg.type', 'hadoop') \\\n    .config('spark.sql.catalog.iceberg.warehouse', 'gs://[YOUR_BUCKET_NAME]/iceberg-warehouse') \\\n    .getOrCreate()",
                "tasks": [
                    {"label": "Configure Iceberg Catalog", "desc": "Set spark.sql.catalog.iceberg properties."},
                    {"label": "Verify Catalog", "desc": "Run spark.sql('SHOW CATALOGS').show()."}
                ]
            },
            {
                "title": "Table Creation & Schema Evolution",
                "subtitle": "Create Iceberg table and alter columns without re-writing historical data.",
                "callout": {
                    "type": "green",
                    "title": "🌱 Schema Evolution",
                    "content": "Iceberg schema changes (add, drop, rename, reorder columns) are metadata-only operations that never rewrite underlying data files."
                },
                "explanation": "Execute DDL commands to create table `iceberg.db.sensors` and evolve schema.",
                "code_lang": "sql",
                "linux_cmd": "-- Create Table\nCREATE TABLE iceberg.db.sensors (\n  device_id STRING,\n  timestamp TIMESTAMP,\n  temperature DOUBLE\n) USING iceberg;\n\n-- Schema Evolution: Add Column\nALTER TABLE iceberg.db.sensors ADD COLUMNS (humidity DOUBLE);",
                "pwsh_cmd": "-- Create Table\nCREATE TABLE iceberg.db.sensors (\n  device_id STRING,\n  timestamp TIMESTAMP,\n  temperature DOUBLE\n) USING iceberg;\n\n-- Schema Evolution: Add Column\nALTER TABLE iceberg.db.sensors ADD COLUMNS (humidity DOUBLE);",
                "tasks": [
                    {"label": "Create Iceberg Table", "desc": "Execute CREATE TABLE iceberg.db.sensors DDL."},
                    {"label": "Evolve Schema", "desc": "Execute ALTER TABLE ADD COLUMNS DDL."}
                ]
            },
            {
                "title": "ACID Transactions (DML: Update, Delete, Merge)",
                "subtitle": "Perform UPDATE, DELETE, and MERGE INTO operations on GCS Iceberg tables.",
                "callout": {
                    "type": "amber",
                    "title": "🛡️ Row-Level ACID Operations",
                    "content": "Iceberg supports positional and equality deletes, making updates and upserts (MERGE INTO) efficient on cloud object storage."
                },
                "explanation": "Execute DML statements directly on data lake tables.",
                "code_lang": "sql",
                "linux_cmd": "-- Insert Records\nINSERT INTO iceberg.db.sensors VALUES ('dev_01', current_timestamp(), 78.5, 45.0);\n\n-- Update Record\nUPDATE iceberg.db.sensors SET temperature = 82.0 WHERE device_id = 'dev_01';\n\n-- Delete Record\nDELETE FROM iceberg.db.sensors WHERE temperature < 50.0;",
                "pwsh_cmd": "-- Insert Records\nINSERT INTO iceberg.db.sensors VALUES ('dev_01', current_timestamp(), 78.5, 45.0);\n\n-- Update Record\nUPDATE iceberg.db.sensors SET temperature = 82.0 WHERE device_id = 'dev_01';\n\n-- Delete Record\nDELETE FROM iceberg.db.sensors WHERE temperature < 50.0;",
                "tasks": [
                    {"label": "Insert Sample Data", "desc": "Execute INSERT INTO statement."},
                    {"label": "Perform UPDATE & DELETE", "desc": "Execute UPDATE and DELETE SQL queries."}
                ]
            },
            {
                "title": "Time Travel & Metadata Inspection",
                "subtitle": "Query historical table snapshots using time travel SQL syntax.",
                "callout": {
                    "type": "purple",
                    "title": "⏳ Time Travel Queries",
                    "content": "Every commit creates an immutable table snapshot. Query historical states using `FOR SYSTEM_TIME AS OF`."
                },
                "explanation": "Inspect metadata table `iceberg.db.sensors.snapshots` and run time travel queries.",
                "code_lang": "sql",
                "linux_cmd": "-- Inspect Snapshots\nSELECT snapshot_id, committed_at, summary FROM iceberg.db.sensors.snapshots;\n\n-- Time Travel Query\nSELECT * FROM iceberg.db.sensors FOR SYSTEM_TIME AS OF '2026-09-07 12:00:00';",
                "pwsh_cmd": "-- Inspect Snapshots\nSELECT snapshot_id, committed_at, summary FROM iceberg.db.sensors.snapshots;\n\n-- Time Travel Query\nSELECT * FROM iceberg.db.sensors FOR SYSTEM_TIME AS OF '2026-09-07 12:00:00';",
                "tasks": [
                    {"label": "Inspect Snapshots Table", "desc": "Query .snapshots metadata table."},
                    {"label": "Execute Time Travel Query", "desc": "Run FOR SYSTEM_TIME AS OF SQL query."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "How does Apache Iceberg achieve atomic commits and time travel capability on object storage?",
                "options": [
                    {"text": "A) By storing data inside SQLite", "correct": False},
                    {"text": "B) By maintaining hierarchical immutable JSON and Avro metadata files tracking table state", "correct": True},
                    {"text": "C) By relying on OS file locking", "correct": False},
                    {"text": "D) By rewriting CSV files on every query", "correct": False}
                ]
            },
            {
                "question": "Which SQL clause allows querying an Iceberg table as it existed at a specific point in time?",
                "options": [
                    {"text": "A) SELECT * FROM table AT TIMELINE 'date'", "correct": False},
                    {"text": "B) SELECT * FROM table FOR SYSTEM_TIME AS OF 'timestamp'", "correct": True},
                    {"text": "C) SELECT * FROM table WHERE snapshot = 1", "correct": False},
                    {"text": "D) SELECT * FROM table REVERT TO 'timestamp'", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 6 ====================
    {
        "id": "Lab6",
        "badge": "6",
        "title": "Lab 6: BigQuery Data Lakes – External Tables & Optimizations",
        "modules": [
            {
                "title": "GCS Dataset Staging & Setup",
                "subtitle": "Copy sensor dataset to Cloud Storage bucket for BigQuery external lake access.",
                "callout": {
                    "type": "purple",
                    "title": "💡 BigQuery Data Lakehouse",
                    "content": "BigQuery can directly query files stored in Cloud Storage (GCS) using External Tables without data ingestion overhead."
                },
                "explanation": "Upload `sensor_data.csv` to your GCS bucket `gs://[YOUR_BUCKET_NAME]/datalake/`.",
                "code_lang": "bash",
                "linux_cmd": "gsutil cp sensor_data.csv gs://[YOUR_BUCKET_NAME]/datalake/sensor_data.csv",
                "pwsh_cmd": "gsutil cp sensor_data.csv gs://[YOUR_BUCKET_NAME]/datalake/sensor_data.csv",
                "tasks": [
                    {"label": "Upload Dataset to GCS", "desc": "Run gsutil cp command."},
                    {"label": "Verify File Path", "desc": "Confirm object path in GCS console."}
                ]
            },
            {
                "title": "Creating BigQuery Dataset",
                "subtitle": "Provision BigQuery dataset container for lakehouse tables.",
                "callout": {
                    "type": "blue",
                    "title": "🗄️ BigQuery Dataset",
                    "content": "Datasets are top-level logical containers that organize tables, views, and external table references."
                },
                "explanation": "Create dataset `sensor_analytics` in region `us-central1`.",
                "code_lang": "bash",
                "linux_cmd": "bq mk --location=us-central1 --dataset sensor_analytics",
                "pwsh_cmd": "bq mk --location=us-central1 --dataset sensor_analytics",
                "tasks": [
                    {"label": "Create Dataset", "desc": "Execute bq mk command."},
                    {"label": "Verify Dataset in BQ Studio", "desc": "Confirm dataset appears in BigQuery SQL Workspace."}
                ]
            },
            {
                "title": "Creating BigQuery External Table",
                "subtitle": "Define an external table over GCS CSV files.",
                "callout": {
                    "type": "amber",
                    "title": "📄 External Tables",
                    "content": "External tables store schema definitions in BigQuery while leaving underlying data files in GCS."
                },
                "explanation": "Execute SQL DDL to create external table `sensor_data_external`.",
                "code_lang": "sql",
                "linux_cmd": "CREATE OR REPLACE EXTERNAL TABLE sensor_analytics.sensor_data_external (\n  device_id STRING,\n  timestamp TIMESTAMP,\n  temperature DOUBLE,\n  humidity DOUBLE\n)\nOPTIONS (\n  format = 'CSV',\n  uris = ['gs://[YOUR_BUCKET_NAME]/datalake/sensor_data.csv'],\n  skip_leading_rows = 1\n);",
                "pwsh_cmd": "CREATE OR REPLACE EXTERNAL TABLE sensor_analytics.sensor_data_external (\n  device_id STRING,\n  timestamp TIMESTAMP,\n  temperature DOUBLE,\n  humidity DOUBLE\n)\nOPTIONS (\n  format = 'CSV',\n  uris = ['gs://[YOUR_BUCKET_NAME]/datalake/sensor_data.csv'],\n  skip_leading_rows = 1\n);",
                "tasks": [
                    {"label": "Create External Table DDL", "desc": "Run CREATE EXTERNAL TABLE SQL query."},
                    {"label": "Query External Table", "desc": "Execute SELECT COUNT(*) FROM sensor_analytics.sensor_data_external."}
                ]
            },
            {
                "title": "Partitioned & Clustered Native Table Ingestion",
                "subtitle": "Ingest raw GCS data into an optimized native table partitioned by DATE and clustered by device_id.",
                "callout": {
                    "type": "green",
                    "title": "⚡ Partitioning & Clustering",
                    "content": "Partitioning divides data by date. Clustering sorts data within partitions. Combined, they drastically reduce bytes scanned and query costs."
                },
                "explanation": "Create native table `sensor_data_optimized` with partitioning and clustering.",
                "code_lang": "sql",
                "linux_cmd": "CREATE OR REPLACE TABLE sensor_analytics.sensor_data_optimized\nPARTITION BY DATE(timestamp)\nCLUSTER BY device_id AS\nSELECT * FROM sensor_analytics.sensor_data_external;",
                "pwsh_cmd": "CREATE OR REPLACE TABLE sensor_analytics.sensor_data_optimized\nPARTITION BY DATE(timestamp)\nCLUSTER BY device_id AS\nSELECT * FROM sensor_analytics.sensor_data_external;",
                "tasks": [
                    {"label": "Create Optimized Native Table", "desc": "Execute CREATE TABLE AS SELECT DDL with PARTITION BY and CLUSTER BY."},
                    {"label": "Inspect Table Details", "desc": "Verify Partitioning and Clustering specs in Table Info tab."}
                ]
            },
            {
                "title": "Performance Benchmark & Teardown",
                "subtitle": "Compare query performance and scanned bytes between External vs Native tables.",
                "callout": {
                    "type": "red",
                    "title": "📊 Performance Metrics",
                    "content": "Native partitioned/clustered tables scan significantly fewer bytes compared to scanning full external CSV files."
                },
                "explanation": "Run identical analytical queries on both tables and observe query execution details.",
                "code_lang": "sql",
                "linux_cmd": "-- Query External Table (Full File Scan)\nSELECT device_id, AVG(temperature) \nFROM sensor_analytics.sensor_data_external \nWHERE timestamp >= '2026-09-01' \nGROUP BY device_id;\n\n-- Query Optimized Native Table (Partition Pruned Scan)\nSELECT device_id, AVG(temperature) \nFROM sensor_analytics.sensor_data_optimized \nWHERE DATE(timestamp) >= '2026-09-01' AND device_id = 'dev_01'\nGROUP BY device_id;",
                "pwsh_cmd": "-- Query External Table (Full File Scan)\nSELECT device_id, AVG(temperature) \nFROM sensor_analytics.sensor_data_external \nWHERE timestamp >= '2026-09-01' \nGROUP BY device_id;\n\n-- Query Optimized Native Table (Partition Pruned Scan)\nSELECT device_id, AVG(temperature) \nFROM sensor_analytics.sensor_data_optimized \nWHERE DATE(timestamp) >= '2026-09-01' AND device_id = 'dev_01'\nGROUP BY device_id;",
                "tasks": [
                    {"label": "Benchmark Bytes Scanned", "desc": "Compare bytes scanned in Query Results > Job Information."},
                    {"label": "Clean Up Dataset", "desc": "Run bq rm -r -f dataset sensor_analytics."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What is the main benefit of using BigQuery External Tables over Cloud Storage?",
                "options": [
                    {"text": "A) Sub-millisecond write latency", "correct": False},
                    {"text": "B) Ability to query data in-place on GCS without paying BigQuery storage costs", "correct": True},
                    {"text": "C) Automatic index generation", "correct": False},
                    {"text": "D) Zero CPU compute cost", "correct": False}
                ]
            },
            {
                "question": "How do Partitioning and Clustering reduce BigQuery query costs?",
                "options": [
                    {"text": "A) By compressing data into ZIP files", "correct": False},
                    {"text": "B) By pruning unneeded partitions and sorting data, minimizing total bytes scanned", "correct": True},
                    {"text": "C) By deleting historical data automatically", "correct": False},
                    {"text": "D) By running queries on local client GPUs", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 7 ====================
    {
        "id": "Lab7",
        "badge": "7",
        "title": "Lab 7: BigQuery Managed Iceberg Tables – Transactional SQL & Time Travel",
        "modules": [
            {
                "title": "GCS Bucket & Connection IAM Authorization",
                "subtitle": "Create Cloud Storage bucket and grant BigQuery Connection service account IAM permissions.",
                "callout": {
                    "type": "purple",
                    "title": "💡 BigQuery Managed Iceberg",
                    "content": "BigQuery Managed Iceberg Tables combine BigQuery's SQL execution engine with Apache Iceberg open storage format on Cloud Storage."
                },
                "explanation": "Create GCS warehouse bucket and grant Storage Object Admin role to BigQuery Connection SA.",
                "code_lang": "bash",
                "linux_cmd": "gsutil mb -l us-central1 gs://[YOUR_PROJECT_ID]-bq-iceberg-warehouse\ngcloud max-file-size=5G ...",
                "pwsh_cmd": "gsutil mb -l us-central1 gs://[YOUR_PROJECT_ID]-bq-iceberg-warehouse\ngcloud max-file-size=5G ...",
                "tasks": [
                    {"label": "Create Warehouse Bucket", "desc": "Create gs://[PROJECT_ID]-bq-iceberg-warehouse bucket."},
                    {"label": "Authorize Connection IAM", "desc": "Grant Storage Object Admin to Connection Service Account."}
                ]
            },
            {
                "title": "Creating BigQuery External Connection",
                "subtitle": "Provision BigQuery Cloud Resource Connection for Apache Iceberg.",
                "callout": {
                    "type": "blue",
                    "title": "🔗 Cloud Resource Connection",
                    "content": "BigQuery uses Cloud Resource Connections to securely authenticate and write Iceberg metadata files directly to GCS buckets."
                },
                "explanation": "Create connection `bq-iceberg-connection` in region `us-central1`.",
                "code_lang": "bash",
                "linux_cmd": "gcloud components update\ngcloud bigquery connections create cloud-resource \\\n  --location=us-central1 \\\n  bq-iceberg-connection",
                "pwsh_cmd": "gcloud components update\ngcloud bigquery connections create cloud-resource `\n  --location=us-central1 `\n  bq-iceberg-connection",
                "tasks": [
                    {"label": "Create Cloud Connection", "desc": "Run gcloud bigquery connections create command."},
                    {"label": "Retrieve SA Email", "desc": "Extract serviceAccountId from connection describe output."}
                ]
            },
            {
                "title": "Provisioning BigQuery Managed Iceberg Table",
                "subtitle": "Execute SQL DDL to create Managed Iceberg Table on GCS.",
                "callout": {
                    "type": "green",
                    "title": "🏗️ Table Format: ICEBERG",
                    "content": "Specifying `table_format='ICEBERG'` and linking your GCS connection creates native Apache Iceberg storage files managed by BigQuery."
                },
                "explanation": "Execute SQL DDL statement in BigQuery SQL workspace.",
                "code_lang": "sql",
                "linux_cmd": "CREATE OR REPLACE TABLE sensor_analytics.managed_iceberg_sensors (\n  device_id STRING,\n  timestamp TIMESTAMP,\n  temperature DOUBLE,\n  status STRING\n)\nWITH CONNECTION `us-central1.bq-iceberg-connection`\nOPTIONS (\n  file_format = 'PARQUET',\n  table_format = 'ICEBERG',\n  storage_uri = 'gs://[YOUR_PROJECT_ID]-bq-iceberg-warehouse/tables/managed_iceberg_sensors'\n);",
                "pwsh_cmd": "CREATE OR REPLACE TABLE sensor_analytics.managed_iceberg_sensors (\n  device_id STRING,\n  timestamp TIMESTAMP,\n  temperature DOUBLE,\n  status STRING\n)\nWITH CONNECTION `us-central1.bq-iceberg-connection`\nOPTIONS (\n  file_format = 'PARQUET',\n  table_format = 'ICEBERG',\n  storage_uri = 'gs://[YOUR_PROJECT_ID]-bq-iceberg-warehouse/tables/managed_iceberg_sensors'\n);",
                "tasks": [
                    {"label": "Execute Table Creation DDL", "desc": "Run CREATE TABLE WITH CONNECTION statement."},
                    {"label": "Verify GCS Files", "desc": "Inspect metadata/ and data/ directories in GCS bucket."}
                ]
            },
            {
                "title": "Transactional DML (INSERT, UPDATE, DELETE, MERGE)",
                "subtitle": "Execute ACID transactional SQL queries directly on BigQuery Managed Iceberg Table.",
                "callout": {
                    "type": "amber",
                    "title": "🔄 Full DML Capabilities",
                    "content": "Unlike standard read-only external tables, BigQuery Managed Iceberg tables support full SQL DML statements (INSERT, UPDATE, DELETE, MERGE)."
                },
                "explanation": "Run DML operations directly in BigQuery Studio.",
                "code_lang": "sql",
                "linux_cmd": "-- Insert Data\nINSERT INTO sensor_analytics.managed_iceberg_sensors VALUES ('dev_01', current_timestamp(), 72.4, 'OK');\n\n-- Update Data\nUPDATE sensor_analytics.managed_iceberg_sensors SET status = 'WARNING' WHERE temperature > 70.0;\n\n-- Delete Data\nDELETE FROM sensor_analytics.managed_iceberg_sensors WHERE status = 'OK';",
                "pwsh_cmd": "-- Insert Data\nINSERT INTO sensor_analytics.managed_iceberg_sensors VALUES ('dev_01', current_timestamp(), 72.4, 'OK');\n\n-- Update Data\nUPDATE sensor_analytics.managed_iceberg_sensors SET status = 'WARNING' WHERE temperature > 70.0;\n\n-- Delete Data\nDELETE FROM sensor_analytics.managed_iceberg_sensors WHERE status = 'OK';",
                "tasks": [
                    {"label": "Run INSERT DML", "desc": "Execute INSERT INTO statement."},
                    {"label": "Run UPDATE & DELETE DML", "desc": "Execute UPDATE and DELETE statements."}
                ]
            },
            {
                "title": "Time Travel & Teardown",
                "subtitle": "Execute time travel queries in BigQuery and clean up resources.",
                "callout": {
                    "type": "red",
                    "title": "🧹 Resource Teardown",
                    "content": "Drop table and connection after completing verification."
                },
                "explanation": "Query historical table states using `FOR SYSTEM_TIME AS OF`.",
                "code_lang": "sql",
                "linux_cmd": "-- Time Travel Query\nSELECT * FROM sensor_analytics.managed_iceberg_sensors FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE);",
                "pwsh_cmd": "-- Time Travel Query\nSELECT * FROM sensor_analytics.managed_iceberg_sensors FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE);",
                "tasks": [
                    {"label": "Execute Time Travel Query", "desc": "Run FOR SYSTEM_TIME AS OF query in BQ Studio."},
                    {"label": "Teardown Resources", "desc": "Drop table and connection."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What key capability do BigQuery Managed Iceberg Tables provide compared to traditional external tables?",
                "options": [
                    {"text": "A) Read-only CSV export", "correct": False},
                    {"text": "B) Native ACID transactional DML support (INSERT, UPDATE, DELETE, MERGE) managed directly by BigQuery engine", "correct": True},
                    {"text": "C) Unlimited free storage", "correct": False},
                    {"text": "D) Zero requirement for GCS storage", "correct": False}
                ]
            },
            {
                "question": "Where are the Apache Iceberg data Parquet files and metadata JSON files stored?",
                "options": [
                    {"text": "A) Inside local client memory", "correct": False},
                    {"text": "B) In the user's Google Cloud Storage bucket configured via BigQuery Connection", "correct": True},
                    {"text": "C) On Dataproc local disk", "correct": False},
                    {"text": "D) In Bigtable", "correct": False}
                ]
            }
        ]
    },

    # ==================== LAB 8 ====================
    {
        "id": "Lab8",
        "badge": "8",
        "title": "Lab 8: Orchestrating Pipelines to Write into BigQuery Managed Iceberg Tables",
        "modules": [
            {
                "title": "Architecture Overview & Prerequisites",
                "subtitle": "Understand Cloud Composer (Airflow) orchestration of Spark Iceberg ETL pipelines.",
                "callout": {
                    "type": "purple",
                    "title": "💡 Airflow & Dataproc Orchestration",
                    "content": "Cloud Composer (Apache Airflow) orchestrates ephemeral Dataproc Spark jobs to ingest, transform, and write data into BigQuery Managed Iceberg tables."
                },
                "explanation": "Review end-to-end architecture combining Cloud Composer, Dataproc, GCS, and BigQuery Managed Iceberg.",
                "code_lang": "bash",
                "linux_cmd": "gcloud services enable composer.googleapis.com dataproc.googleapis.com bigquery.googleapis.com",
                "pwsh_cmd": "gcloud services enable composer.googleapis.com dataproc.googleapis.com bigquery.googleapis.com",
                "tasks": [
                    {"label": "Enable GCP Orchestration APIs", "desc": "Confirm Cloud Composer, Dataproc, and BigQuery APIs are enabled."},
                    {"label": "Review Architecture Diagram", "desc": "Understand airflow DAG task dependencies."}
                ]
            },
            {
                "title": "PySpark ETL Script (`spark_iceberg_etl_lab8.py`)",
                "subtitle": "Inspect PySpark ETL logic appending data to BigQuery Managed Iceberg tables.",
                "callout": {
                    "type": "blue",
                    "title": "🐍 PySpark Iceberg Writer",
                    "content": "PySpark uses the Iceberg catalog to write Parquet data files and commit new metadata manifests into GCS."
                },
                "explanation": "Review PySpark script that loads telemetry from GCS and appends to Iceberg catalog.",
                "code_lang": "python",
                "linux_cmd": "# spark_iceberg_etl_lab8.py snippet\nfrom pyspark.sql import SparkSession\n\nspark = SparkSession.builder \\\n    .appName('Spark-Iceberg-ETL-Lab8') \\\n    .getOrCreate()\n\n# Read Raw Data\nraw_df = spark.read.csv('gs://[PROJECT_ID]-code-bin/data/sensor_data.csv', header=True)\n\n# Write to BigQuery Managed Iceberg Table\nraw_df.write \\\n    .format('iceberg') \\\n    .mode('append') \\\n    .save('iceberg_catalog.sensor_analytics.managed_iceberg_sensors')",
                "pwsh_cmd": "# spark_iceberg_etl_lab8.py snippet\nfrom pyspark.sql import SparkSession\n\nspark = SparkSession.builder \\\n    .appName('Spark-Iceberg-ETL-Lab8') \\\n    .getOrCreate()\n\n# Read Raw Data\nraw_df = spark.read.csv('gs://[PROJECT_ID]-code-bin/data/sensor_data.csv', header=True)\n\n# Write to BigQuery Managed Iceberg Table\nraw_df.write \\\n    .format('iceberg') \\\n    .mode('append') \\\n    .save('iceberg_catalog.sensor_analytics.managed_iceberg_sensors')",
                "tasks": [
                    {"label": "Verify PySpark Script", "desc": "Check DataFrame read and write.format('iceberg') mode."},
                    {"label": "Upload Script to GCS", "desc": "Stage script in GCS code bucket."}
                ]
            },
            {
                "title": "Designing Apache Airflow DAG (`dataproc_workflow_dag.py`)",
                "subtitle": "Configure Airflow DAG with DataprocSubmitJobOperator.",
                "callout": {
                    "type": "green",
                    "title": "⚙️ Ephemeral Dataproc Clusters",
                    "content": "DataprocSubmitJobOperator or DataprocWorkflowTemplateInstantiateOperator spins up ephemeral clusters on-demand for cost efficiency."
                },
                "explanation": "Review Airflow DAG file orchestrating Dataproc PySpark job submission.",
                "code_lang": "python",
                "linux_cmd": "# dataproc_workflow_dag.py snippet\nfrom airflow import DAG\nfrom airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator\nfrom datetime import datetime\n\npyspark_job = {\n    'reference': {'project_id': '[PROJECT_ID]'},\n    'placement': {'cluster_name': 'ephemeral-etl-cluster'},\n    'pyspark_job': {'main_python_file_uri': 'gs://[PROJECT_ID]-code-bin/spark_iceberg_etl_lab8.py'}\n}\n\nwith DAG('dataproc_iceberg_etl_dag', start_date=datetime(2026, 1, 1), schedule_interval=None) as dag:\n    run_etl = DataprocSubmitJobOperator(\n        task_id='run_spark_iceberg_etl',\n        job=pyspark_job,\n        region='us-central1'\n    )",
                "pwsh_cmd": "# dataproc_workflow_dag.py snippet\nfrom airflow import DAG\nfrom airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator\nfrom datetime import datetime\n\npyspark_job = {\n    'reference': {'project_id': '[PROJECT_ID]'},\n    'placement': {'cluster_name': 'ephemeral-etl-cluster'},\n    'pyspark_job': {'main_python_file_uri': 'gs://[PROJECT_ID]-code-bin/spark_iceberg_etl_lab8.py'}\n}\n\nwith DAG('dataproc_iceberg_etl_dag', start_date=datetime(2026, 1, 1), schedule_interval=None) as dag:\n    run_etl = DataprocSubmitJobOperator(\n        task_id='run_spark_iceberg_etl',\n        job=pyspark_job,\n        region='us-central1'\n    )",
                "tasks": [
                    {"label": "Review DAG Structure", "desc": "Check task dependencies and Operator parameters."},
                    {"label": "Verify Schedule Interval", "desc": "Confirm schedule_interval and start_date settings."}
                ]
            },
            {
                "title": "Deploying DAG & Monitoring Execution",
                "subtitle": "Deploy DAG to Cloud Composer environment and monitor task execution.",
                "callout": {
                    "type": "amber",
                    "title": "🚀 Cloud Composer Deployment",
                    "content": "Copying Python DAG files into the Composer GCS `dags/` bucket automatically syncs the workflow to Airflow."
                },
                "explanation": "Upload `dataproc_workflow_dag.py` to the Cloud Composer DAGs bucket and trigger in Airflow UI.",
                "code_lang": "bash",
                "linux_cmd": "COMPOSER_DAG_BUCKET=$(gcloud composer environments describe [COMPOSER_ENV_NAME] --region=us-central1 --format=\"value(config.dagGcsPrefix)\")\ngsutil cp dataproc_workflow_dag.py $COMPOSER_DAG_BUCKET/",
                "pwsh_cmd": "$COMPOSER_DAG_BUCKET=(gcloud composer environments describe [COMPOSER_ENV_NAME] --region=us-central1 --format=\"value(config.dagGcsPrefix)\")\ngsutil cp dataproc_workflow_dag.py $COMPOSER_DAG_BUCKET/",
                "tasks": [
                    {"label": "Upload DAG to Composer Bucket", "desc": "Run gsutil cp to sync DAG to Airflow bucket."},
                    {"label": "Trigger DAG in Airflow UI", "desc": "Open Airflow UI and trigger run_spark_iceberg_etl task."}
                ]
            },
            {
                "title": "Verifying Appended Data & Teardown",
                "subtitle": "Query BigQuery Managed Iceberg table to verify newly appended data and clean up.",
                "callout": {
                    "type": "red",
                    "title": "✅ Pipeline Verification",
                    "content": "Verify that newly appended records are immediately queryable in BigQuery with updated snapshot IDs."
                },
                "explanation": "Run SQL query in BigQuery to confirm appended rows.",
                "code_lang": "sql",
                "linux_cmd": "-- Confirm Appended Rows in BigQuery\nSELECT COUNT(*) FROM sensor_analytics.managed_iceberg_sensors;",
                "pwsh_cmd": "-- Confirm Appended Rows in BigQuery\nSELECT COUNT(*) FROM sensor_analytics.managed_iceberg_sensors;",
                "tasks": [
                    {"label": "Verify Row Count in BigQuery", "desc": "Run SELECT COUNT(*) SQL query in BigQuery Studio."},
                    {"label": "Teardown Composer Environment", "desc": "Clean up Cloud Composer and Dataproc resources."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "Why are ephemeral Dataproc clusters ideal for automated Airflow ETL DAGs?",
                "options": [
                    {"text": "A) Ephemeral clusters run permanently", "correct": False},
                    {"text": "B) Clusters are created on-demand for job execution and deleted immediately after completion, eliminating idle costs", "correct": True},
                    {"text": "C) Ephemeral clusters bypass cloud security", "correct": False},
                    {"text": "D) Ephemeral clusters do not require Cloud Storage", "correct": False}
                ]
            },
            {
                "question": "Where must Apache Airflow DAG files be uploaded in Google Cloud Composer?",
                "options": [
                    {"text": "A) To the designated dags/ folder in the environment's Cloud Storage bucket", "correct": True},
                    {"text": "B) Directly into Dataproc master nodes", "correct": False},
                    {"text": "C) Inside BigQuery datasets", "correct": False},
                    {"text": "D) To local client /tmp folder", "correct": False}
                ]
            }
        ]
    },

    # ==================== CAPSTONE PROJECT ====================
    {
        "id": "capstone_project",
        "badge": "★",
        "title": "Capstone Project: Walmart Retail Big Data Pipeline on GCP",
        "modules": [
            {
                "title": "System Architecture & Terraform Provisioning",
                "subtitle": "Provision GCP infrastructure using Infrastructure as Code (IaC) with Terraform.",
                "callout": {
                    "type": "purple",
                    "title": "🏢 Enterprise Retail Architecture",
                    "content": "This capstone implements an end-to-end streaming and batch data lakehouse architecture handling Orders, Inventory, and Customer events using Pub/Sub, Dataflow, PySpark, Iceberg, and BigQuery."
                },
                "explanation": "Apply Terraform configuration (`main.tf`) to provision Pub/Sub topics (`orders-events`, `inventory-events`, `customer-events`), GCS buckets (`iceberg-raw`, `iceberg-curated`), and BigQuery dataset `retail_analytics`.",
                "code_lang": "bash",
                "linux_cmd": "cd capstone_project/terraform\nterraform init\nterraform apply -var=\"project_id=[YOUR_PROJECT_ID]\" -auto-approve",
                "pwsh_cmd": "cd capstone_project/terraform\nterraform init\nterraform apply -var=\"project_id=[YOUR_PROJECT_ID]\" -auto-approve",
                "tasks": [
                    {"label": "Run Terraform Init", "desc": "Initialize HashiCorp GCP Provider plugins."},
                    {"label": "Apply Infrastructure Config", "desc": "Provision Pub/Sub topics, GCS buckets, and BigQuery dataset."}
                ]
            },
            {
                "title": "Streaming Telemetry Ingestion (`mock_events_publisher.py`)",
                "subtitle": "Publish simulated retail transactions into Pub/Sub topics.",
                "callout": {
                    "type": "blue",
                    "title": "🛒 Real-Time Streaming Events",
                    "content": "Simulate high-velocity retail sales, stock level changes, and customer transactions across multiple store IDs."
                },
                "explanation": "Execute `mock_events_publisher.py` to stream continuous JSON telemetry events into Pub/Sub.",
                "code_lang": "python",
                "linux_cmd": "python capstone_project/publisher/mock_events_publisher.py \\\n  --project_id=[YOUR_PROJECT_ID] \\\n  --num_events=500",
                "pwsh_cmd": "python capstone_project/publisher/mock_events_publisher.py `\n  --project_id=[YOUR_PROJECT_ID] `\n  --num_events=500",
                "tasks": [
                    {"label": "Inspect JSON Schemas", "desc": "Review order_event.json and inventory_event.json schemas."},
                    {"label": "Run Mock Publisher", "desc": "Stream 500 synthetic retail events to Pub/Sub."}
                ]
            },
            {
                "title": "Dataflow Streaming Pipeline to Iceberg Raw Storage",
                "subtitle": "Deploy Apache Beam streaming pipeline (`streaming_pipeline.py`) to Dataflow.",
                "callout": {
                    "type": "green",
                    "title": "🌊 Dataflow Ingestion Layer",
                    "content": "Dataflow validates JSON schemas, converts records into Beam NamedTuples, and streams data into GCS Raw Iceberg storage."
                },
                "explanation": "Deploy `streaming_pipeline.py` on Cloud Dataflow.",
                "code_lang": "python",
                "linux_cmd": "python capstone_project/dataflow/streaming_pipeline.py \\\n  --runner=DataflowRunner \\\n  --project=[YOUR_PROJECT_ID] \\\n  --region=us-central1 \\\n  --temp_location=gs://[YOUR_PROJECT_ID]-iceberg-raw/temp \\\n  --staging_location=gs://[YOUR_PROJECT_ID]-code-bin/staging",
                "pwsh_cmd": "python capstone_project/dataflow/streaming_pipeline.py `\n  --runner=DataflowRunner `\n  --project=[YOUR_PROJECT_ID] `\n  --region=us-central1 `\n  --temp_location=gs://[YOUR_PROJECT_ID]-iceberg-raw/temp `\n  --staging_location=gs://[YOUR_PROJECT_ID]-code-bin/staging",
                "tasks": [
                    {"label": "Submit Dataflow Streaming Job", "desc": "Deploy streaming pipeline to DataflowRunner."},
                    {"label": "Verify GCS Raw Iceberg Tables", "desc": "Confirm Iceberg metadata files arrive in gs://[PROJECT_ID]-iceberg-raw."}
                ]
            },
            {
                "title": "Batch ETL & Curation with PySpark on Dataproc",
                "subtitle": "Run `spark_etl_job.py` on Dataproc to aggregate Raw into Curated Iceberg storage.",
                "callout": {
                    "type": "amber",
                    "title": "⚡ Spark Batch Curation",
                    "content": "PySpark batch jobs read Raw Iceberg storage, perform deduplication, aggregate daily sales revenue by store, and write to Curated Iceberg storage."
                },
                "explanation": "Submit PySpark batch curation job on Dataproc.",
                "code_lang": "bash",
                "linux_cmd": "gcloud dataproc jobs submit pyspark capstone_project/dataproc/spark_etl_job.py \\\n  --cluster=ephemeral-dataproc-cluster \\\n  --region=us-central1 \\\n  -- --project_id=[YOUR_PROJECT_ID]",
                "pwsh_cmd": "gcloud dataproc jobs submit pyspark capstone_project/dataproc/spark_etl_job.py `\n  --cluster=ephemeral-dataproc-cluster `\n  --region=us-central1 `\n  -- --project_id=[YOUR_PROJECT_ID]",
                "tasks": [
                    {"label": "Run PySpark Batch Curation", "desc": "Execute spark_etl_job.py on Dataproc."},
                    {"label": "Verify Curated Tables", "desc": "Confirm curated_sales_daily table is generated in GCS Curated bucket."}
                ]
            },
            {
                "title": "End-to-End Orchestration & BigQuery Analytics",
                "subtitle": "Orchestrate workflow with Airflow (`orchestration_dag.py`) and query in BigQuery.",
                "callout": {
                    "type": "purple",
                    "title": "📊 Retail Analytics Workspace",
                    "content": "Execute analytical SQL queries in BigQuery over external and managed Iceberg tables to track daily revenue and store stock levels."
                },
                "explanation": "Deploy Airflow DAG to Cloud Composer and run business intelligence SQL queries in BigQuery.",
                "code_lang": "sql",
                "linux_cmd": "-- Daily Revenue Aggregation Query in BigQuery\nSELECT store_id, SUM(total_sales_amount) as daily_revenue\nFROM retail_analytics.sales_daily_external\nGROUP BY store_id\nORDER BY daily_revenue DESC;",
                "pwsh_cmd": "-- Daily Revenue Aggregation Query in BigQuery\nSELECT store_id, SUM(total_sales_amount) as daily_revenue\nFROM retail_analytics.sales_daily_external\nGROUP BY store_id\nORDER BY daily_revenue DESC;",
                "tasks": [
                    {"label": "Deploy Airflow Orchestration DAG", "desc": "Copy orchestration_dag.py to Composer DAGs bucket."},
                    {"label": "Run BigQuery Lakehouse Queries", "desc": "Execute analytical SQL queries over Iceberg tables in BQ Studio."}
                ]
            },
            {
                "title": "Infrastructure Teardown & Cleanup",
                "subtitle": "Destroy all GCP resources via Terraform to prevent cloud costs.",
                "callout": {
                    "type": "red",
                    "title": "⚠️ Complete Teardown",
                    "content": "Execute `terraform destroy` to tear down Pub/Sub topics, GCS buckets, and BigQuery datasets."
                },
                "explanation": "Clean up all cloud resources using Terraform.",
                "code_lang": "bash",
                "linux_cmd": "cd capstone_project/terraform\nterraform destroy -var=\"project_id=[YOUR_PROJECT_ID]\" -auto-approve",
                "pwsh_cmd": "cd capstone_project/terraform\nterraform destroy -var=\"project_id=[YOUR_PROJECT_ID]\" -auto-approve",
                "tasks": [
                    {"label": "Run Terraform Destroy", "desc": "Execute terraform destroy command."},
                    {"label": "Verify Teardown", "desc": "Confirm zero active resources remaining in GCP Console."}
                ]
            }
        ],
        "quiz": [
            {
                "question": "What design architecture does the Walmart Retail Big Data Pipeline use to unify real-time ingestion with analytical querying?",
                "options": [
                    {"text": "A) Monolithic Relational Database", "correct": False},
                    {"text": "B) Lakehouse Architecture combining Pub/Sub + Dataflow (Streaming Raw) with Spark + BigQuery Iceberg (Batch Curated)", "correct": True},
                    {"text": "C) Manual CSV Export via FTP", "correct": False},
                    {"text": "D) SQLite File Storage", "correct": False}
                ]
            },
            {
                "question": "Why is Infrastructure as Code (Terraform) essential for enterprise Big Data GCP pipelines?",
                "options": [
                    {"text": "A) Terraform makes PySpark run faster", "correct": False},
                    {"text": "B) Terraform allows reproducible, version-controlled, automated cloud environment deployment and teardown", "correct": True},
                    {"text": "C) Terraform replaces Apache Beam", "correct": False},
                    {"text": "D) Terraform removes the need for GCP IAM roles", "correct": False}
                ]
            }
        ]
    }
]

def build_all():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for lab in labs_data:
        lab_id = lab['id']
        lab_dir = os.path.join(root_dir, lab_id)
        os.makedirs(lab_dir, exist_ok=True)
        
        target_file = os.path.join(lab_dir, 'Lab.html')
        html_code = generate_labs.get_template(
            lab_id=lab['id'],
            lab_badge=lab['badge'],
            lab_title=lab['title'],
            modules=lab['modules'],
            quiz_questions=lab['quiz']
        )
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(html_code)
        
        print(f"Successfully generated {target_file}")

if __name__ == '__main__':
    build_all()
