# Big Data
Big Data is not a programming language, software, or framework. It is a category of problems involving data that is difficult to store, process, or analyze efficiently using conventional approaches.

Apache Spark, Databricks, Kafka, Hadoop, and other technologies are different solutions to problems that arise when working with data at scale.

The most important thing is to understand why these technologies exist and how they fit together, rather than memorizing their names.


###### Three major characteristics of Big Data
- Volume: There is a large amount of data to store and process.

- Velocity: Data arrives rapidly, possibly millions of events per second.

- Variety: Data comes in different formats: database records, JSON, logs, images, videos, sensor readings, etc.

#### Why do we need Big Data technologies?
There are two broad approaches to increasing computing capacity.

- Vertical scaling: Replacing an EC2 instance with one that has more CPU cores and RAM.
- Horizontal scaling: Using ten EC2 instances together to process a dataset.
The second approach introduces a new problem: how do we coordinate those ten machines?

Someone must decide which machine processes which data, combine the results, and handle failures.

This is where distributed computing frameworks such as Apache Spark become useful

## APACHE SPARK
Spark is an open-source distributed data-processing engine. It coordinates computation across multiple CPU cores or machines so large datasets can be processed efficiently.

Think of Spark as a more powerful processing environment for operations such as:
- Filtering billions of records.
- Joining enormous datasets.
- Grouping and aggregating data.
- Preparing training datasets for machine learning.
- Processing continuously arriving data.
Spark supports Python, Scala, Java, and SQL, among other interfaces. The Python API is called PySpark

How does Spark work internally?


The important concepts are:
1. Driver: The process that coordinates your Spark application.
2. Workers and executors: Machines and processes that carry out computations.
3. Partitions: Pieces of a dataset that can be processed independently.
4. Tasks: Units of work assigned to executor processes.
5. Shuffle: Movement of data between partitions, often required for joins and group-by operations.

## Databricks
*Databricks is a commercial cloud platform* for data engineering, analytics, and machine learning. It provides managed infrastructure and integrates tools such as Spark, Delta Lake, MLflow, and data governance services.


Imagine you want to use Spark to process 10 TB of data on AWS.

Without Databricks, you may need to provision machines, configure Spark, manage dependencies, schedule jobs, monitor failures, and maintain the infrastructure yourself.

With Databricks, much of that infrastructure management is handled by the platform. You can write Python or SQL in a notebook, configure compute resources, and execute distributed data-processing jobs.

Databricks also provides capabilities beyond Spark, such as SQL analytics, workflow orchestration, model management, and serving

Spark is a technology you can use independently. Databricks is one platform that makes Spark and related technologies easier to use in production.

# Where is big data stored?
Big Data systems commonly separate storage from processing.

There are three important concepts.

1. Data Lake
A repository that stores raw and processed data in formats such as CSV, JSON, Parquet, images, and logs. AWS S3 is commonly used as its underlying storage.

2. Data Warehouse
A system optimized for SQL analytics over large datasets. Examples include Snowflake, Google BigQuery, and Amazon Redshift.


3. Data Lakehouse
An architecture combining the flexible, relatively inexpensive storage of data lakes with useful database and warehouse capabilities such as reliable table updates, transactions, and governance.


#### spark, pyarrow, parquet
Spark already knows how to read Parquet files from disk and process them without Arrow. You only need Arrow when data has to jump from Spark's JVM world into Python tools like Pandas. PyArrow makes that transfer faster. Also, PyArrow itself can read Parquet into Python, but that's separate from Spark reading Parquet. Parquet is for storage; Arrow is for fast in-memory exchange between systems. They solve different problems.

PyArrow is not just for copying Parquet files from disk into RAM. It implements Arrow, which is a standardized in-memory column format for fast sharing between systems like Spark and Pandas. Sometimes it reads Parquet files, but sometimes it just moves data already in memory, and sometimes you use it in pure Python without Spark at all. The key thing is that Arrow is not the mandatory middle step between Parquet and RAM; it's a way to represent and exchange columnar data efficiently when different tools need to work together.

###### Question: So the data which is already present in RAM, which is used by Pandas, looks different when it's used in Spark, and that conversion is done by Arrow

Answer: 
Yes, exactly. You've understood the main idea. There is just one technical correction: Arrow doesn't perform every conversion automatically. It defines a standardized in-memory representation, and libraries such as PyArrow implement the conversion.

The same logical data can have different physical representations in RAM.

For example, consider three ages: 25, 30, 35.

Spark: Typically represents the data using its JVM-based internal structures, often optimized for distributed and columnar processing.

Pandas: Represents the data using structures such as NumPy arrays or Arrow-backed arrays.

Arrow: Defines a standard columnar memory layout that allows the two environments to exchange data efficiently.

###### Question: So Spark doesn't take and process data in form of Parquet files directly

Answer:
Good question. It reads Parquet directly from disk, yes. But not literally compute on the compressed bytes, as they are stored in the file. It reads the Parquet column chunks, then it decompresses and decodes them into its own in-memory columnar structures, and that is what it computes on. So, “directly” is true for reading Parquet, but not for computing on the raw on-disk representation. That decode-and-layout step is what turns “storage-optimized columns” into “compute-optimized columns.

Apache Arrow's in-memory format is columnar, so data represented in that format must follow a column-oriented layout.

However, the original data doesn't have to be columnar. PyArrow can convert row-oriented data into its columnar representation.

For example, PyArrow can take a Python list of dictionaries (row-oriented data) and create an Arrow Table.


### Data sources and formats
Unstructured data is more flexible, but has too much parsing overhead

Semi-structured data:
XML, JSON

Structured data has more efficient storage and performance, least parsing overhead

Parquet is a structured data format

Row wise storage are good for application databases because it requires reads, inserts
Best use- OLTP/Transactional apps

##### OLTP (Online Transaction Processing)
It's a database architecture and workload type designed for high-volume, short, real-time read and write operations(placing an order, updating a user profile, or recording a payment)

*Core characterstics*
1. Short, frequent transactions: Most queries touch a small number of rows (often via primary keys or B-tree indexes) and complete in milliseconds.

Heavy write and update activity: Unlike analytics workloads that mostly read historical data, OLTP systems constantly INSERT, UPDATE, and DELETE live records.

Normalized schemas (typically 3NF): Tables are split across relational entities (e.g., users, orders, order_items, payments) to eliminate data duplication and prevent update anomalies during concurrent writes.

ACID guarantees: Transactions are Atomic, Consistent, Isolated, and Durable—meaning a partial failure rolls back cleanly and concurrent updates do not corrupt state.

Row-oriented storage: Rows are stored contiguously on disk/memory pages, making point lookups and single-record writes fast.

###### Typical Architecture & Trade-offs
In a standard application backend, an OLTP database acts as the system of record:

1. Application writes hit the OLTP primary instance, which appends changes to a Write-Ahead Log (WAL) for durability and updates in-memory buffer pools and indexes.

2. Read replicas handle scaling read traffic or offloading lighter reporting queries without contending with primary writes.

3. Analytical workloads are usually decoupled via CDC (Change Data Capture) or ETL/ELT pipelines into an OLAP store so heavy scans do not slow down live user transactions


##### OLAP (Online Analytical Processing)
It's a database architecture and workload type built for complex, read-heavy analytical queries - such as aggregations, cohort analysis, trend rollups, and multi-dimensional slicing—across large volumes of historical data.

While OLTP powers live application state (INSERT/UPDATE/DELETE on individual records), OLAP answers business and analytical questions over millions or billions of rows without impacting production transactions.


Core Characteristics of OLAP
Read-heavy, scan- and aggregate-intensive: Queries typically read many rows across a few columns (SUM, COUNT, AVG, GROUP BY, window functions) rather than doing single-row primary-key lookups.

Columnar storage: Data is stored column-by-column rather than row-by-row. A query touching 3 out of 100 columns only reads data blocks for those 3 columns, cutting I/O dramatically and enabling high compression (e.g., run-length, dictionary encoding).

Denormalized schemas (Star / Snowflake): Fact tables (events, transactions, metrics) connect to dimension tables (time, user, product, region), reducing expensive multi-way joins at query time.

Batch or micro-batch ingestion: Data usually lands via ETL/ELT pipelines or Change Data Capture (CDC) from OLTP systems, optimized for bulk appends/loads rather than frequent small row updates.

Massive scale & MPP / vectorized execution: Designed to scan large datasets across distributed workers or vectorized CPU/GPU execution engines.

###### Why Most OLAP Still Runs on CPUs
GPUs lose out mostly because moving data to the GPU is a major bottleneck and GPUs are expensive relative to how fast vectorized CPUs already are for general SQL analytics—with VRAM ceilings and messy string/join/branching logic making it harder outside specialized niches.