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
If Queries are like few large operations involving *subset* of all columns. Rather than small operations involving whole rows for which we use OLTP processing

FRAGMENTED MEMORY ACCESS PATTERN

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


### Apache Parquet
1. Initial effort by twitter & cloudera
2. Open source storage format
3. Widely used in Spark/Hadoop ecosystem

##### How does Parquet files look like
- On disk, usually not a single file

f you open a .parquet file in a text editor or cat it in a terminal, it looks like compressed binary gibberish—except for the magic bytes PAR1 at the very beginning and end of the file.Structurally, inside that binary stream, a Parquet file is organized into Row Groups, Column Chunks, Pages, and a Footer at the end so readers can jump straight to metadata before reading data.

###### Byte-Level Layout of a Parquet File
From start to finish on disk or in object storage, a Parquet file follows this layout:

Header (PAR1 — 4 bytes): Identifies the file as Parquet.

Row Groups (1 or more): Horizontal batches of rows (commonly tens of thousands to millions of rows per row group).

Inside each row group, there is one Column Chunk per column.

Each column chunk is split into Pages (data pages, dictionary pages, index pages), where values are first encoded (e.g., plain, dictionary, run-length encoding / bit-packing) and then compressed (e.g., Snappy, Zstandard, Gzip).

Footer: Stored at the end of the file (written after all row groups are flushed). It contains the schema, row group count, byte offsets/sizes of every column chunk, and column statistics (min, max, null_count).

Footer Length (4 bytes) + PAR1 (4 bytes): Placed at the very tail so a reader can seek to the end of the file, read the 4-byte length, jump backward to read the footer, and then selectively fetch only the needed byte ranges.

##### Parquet: Encoding schemes
###### PLAIN
- Fixed-width: Back-to-back
- Non fixed-width: length prefixed

###### RLE_DICTIONARY
- Run-length encoding + bit-packing + Dictioanry compression
- Assumes duplicate and repeated value

#### Optimization
##### Dictionary Encoding
- Smaller files means less I/O
- Note: Single dictionary per column chunk, There is a size limit to the dictionary

If the dictionary gets too big -> Automatic fallback to PLAIN
ie. rest of the data is encoded using the plain encoding format and it's gonna miss all the compression opportunities

We can
- Increase max dictionary size
- Decrease row-group size

##### Page Compression
1. Compression of entire pages
- Compression schemes(snappy, gzip, lzo...)
- Decompression speed vs I/O saving trade-off

##### Predicate Pushdown
SELECT * FROM table where x > 5 ;

Row-group 0: x: [min:0, max: 9]
Row-group 1: x: [min:3, max: 7]
Row-group 2: x: [min:1, max: 4]
They are all stored in the footer of the parquet file

The first thing we do while reading a parquet file is *READING THE FOOTER*
We will have this metadata at our disposal and we can leverage this metadata for row-group skipping

Row groiup can be 128MB, So skipping it can help us immensly

- Leverage min/max staistics
    spark.sql.parquet.filterPushdown

- Doesn't work well on unsorted data
What to do? Presort data on predicate columns

- Use typed predicates
Eg : use actual longs in predicate instead of ints fro long columns


- Dictionary filtering
SELECT * FROM table WHERE x=5;

Row-group 2: x: [min:1, max: 4]
Row-group 0: x: [min:0, max: 9]
Row-group 1: x: [min:3, max: 7]

##### Partitioning
Embed the preicates we have into the actual directory structure of the file

If we know predicates before workhand

##### Avoid many small files
1. Foe every file
- set up internal data structure
- Instantiate reader objects
- Fetch file
- Parse Parquet metadata

The overhead can contribute significantly to our total query time

2. Watchout for incremental workload output!
Eg: ETL every hour

3. Manual reparti tioning
    - Can we automate this optimization?
    - What about concurrent access?

4. We need isolation of Operations(i.e. ACID transactions)

##### Delta Lake
1. Open-source storage layer on top of parquet in spark
    - ACID Transactions
    - Time Travel (versionaing via WAL-Write Ahead Log)


##### Avoid few huge parquet files
1. SELECT count (*) on 250GB dataset
  - 250 partitions(~iGB each)
    5 mins
  - 1 HUge partition(250GB)
    1 hour

Because the footer becomes huge, we will have a lots of row groups, lots of metadata and the footer processing is not optimized for speed


# Redshift, Snowflake, Databricks and spark
Spark, Redshift, and Snowflake overlap significantly in the computations they perform.

All three can filter data, join tables, aggregate millions or billions of records, and distribute computations across multiple machines.

The main difference is:
- Apache Spark: Primarily a general-purpose distributed processing engine. It usually reads data from external storage, processes it, and writes results somewhere.
- Amazon Redshift and Snowflake: Complete analytical database platforms. They provide distributed processing engines plus persistent data storage, table management, and database services.
But there's one additional distinction: Redshift and Snowflake are particularly optimized for analytical SQL queries, whereas Spark supports broader processing workloads, including complex data pipelines and distributed machine learning.

So your understanding is correct: they overlap in processing capabilities, but Redshift and Snowflake provide more integrated database functionality.


Databricks competes with Redshift and Snowflake for analytics and warehousing, though each is stronger in different areas. They overlap, but they're not identical. So companies choose among them based on their needs. Does that answer it?

Yes. Databricks competes with Amazon Redshift and Snowflake, particularly in large-scale SQL analytics and data warehousing.

However, their strengths differ:
- Databricks: Strong in data engineering, Apache Spark, machine learning, AI, and lakehouse architecture.
- Snowflake: Strong in managed SQL analytics, data warehousing, and data sharing.
- Amazon Redshift: Strong in SQL analytics and integration with the AWS ecosystem.
All three can store or manage data, execute distributed SQL queries, and support analytical workloads.

The important difference is that Databricks also provides a broader environment for Spark-based data processing and ML workflows.

So yes, they are competitors, but not identical products. Companies choose among them based on their workloads, existing infrastructure, and requirements


# Story/ History
Say our comapany has data: Sales, Transactions, Logs, Events and we wantd to process it for analytics and engineering

So we write SQL, Python, Java and we run it on A SINGLE MACHINE

But data started to grow: Structured + unstructured images, videos, Pdfs...

Buying bigger machines works for a while until we can't. Also a single point of failure is present


Then comes a solution from Google -> Hadoop

But it didn't solved everything because of one big issue-
When we assigned work to multiple machines, each machine was reading and writing data from the disk which was "slow".

So hadoop is scalable and falut tolerant but slow

### How to speed up Hadoop?

Spark...

The main idea was same - Distribute the data between multiple machines, but instead of reading and writing to discs, spark is 
going to keep the data in the memory whenever it's possible

New problems arrived...
this time it was not the technology itself but rather "Who was able to use it"

Spark was only for big data experts that were able to develop using scala and java. 
But data science was explaoding, universities were teaching pyhton.
Python libraries like numpy, pytorch, scikit-learn etc were exploding. So data scientists prefer only python to do their work and there was a gap between these two worlds

- Big Data engineers that uses spark
- Big data scientists were using python

So Pyspark was introduces to let python users like data scientists work with spark environment

So anyone knowing python is welcomed to use spark

### But the operational side was a real nightmare
We have to go manage the infrastructure, configure the clusters, handle the scaling, the security, the failures. So the projects were really slow

Our goal was to focus on building the pipelines and projects, not babysitting the clusters. Everything was scattered, the storage, the notebooks, the scheduling, the monitoring

Because of all those issues, in 2013, the creators of sparkstarted thinnking about a bigger idea.

How about we built databricks where a dedicated team is going
to handle all the complex infrastructure and the nightmare that comes with it completely behind the scenes(Manage the clusters, connecting with cloud storage, integrating the notebooks, configuring the environments) and putting everything in one unified platform. And we customers, data teams, can finally focus on bulding 
data pipelines, running the analysis, delivering all the projects



# Spark

Process 1: Python
Runs your PySpark code
Creates DataFrames, defines transformations, submits jobs
          |
          |
          |
Py4J communication
          |
          |
          |
Process 2: Java (JVM)
Runs Spark's driver-side engine
Plans tasks, schedules work, executes Spark operations
          |
          |
          |
Local execution
          |
Spark executor threads
Process data using your laptop's CPU cores and RAM


Normally Spark keeps the data in the JVM and your Python side mostly holds a plan and small results, not a full copy. Picture it like Python sends instructions to JVM, JVM reads and aggregates the data, and only small answers come back to Python to show or store. But if you pull everything into Python with collect or toPandas, then yes, you'll have another copy in Python memory and that can blow up RAM. Also, Python UDFs can copy chunks of data to Python worker processes, which adds overhead. So, it doesn't automatically double memory, but some operations can.

Python Process                  JVM Process
┌─────────────────┐           ┌─────────────────────┐
│ Python code     │           │ Spark engine        │
│ DataFrame plan  │ ────────► │ Reads Parquet data  │
│ Small metadata  │           │ Processes partitions│
└─────────────────┘           └─────────────────────┘

But there are exceptions where additional copies can exist.
- If you call df.collect() or df.toPandas(), the results are transferred into Python memory. This can substantially increase RAM usage.
- If you use Python UDFs, data is transferred between JVM and Python worker processes, creating additional memory overhead.
- If you create a Spark DataFrame from an existing Pandas DataFrame, both representations may temporarily occupy memory.


##### DataFrame 
Databases store tables, they optimize for query and storage, 
but if we are using databases we are interacting with data 
by using only SQL. So when the transformation becomes complex, SQL becomes really long and nested and hard to manage.

We don't havae the flexibility and modularity like python. Also leess advanced analytics

So databases are optimized for different job(storage and query), not for advanced analytics and data processing

In both cases, excel and dataabses our table is living outside of
our python code and we can't fully use programming logic on it

A Dataframe will be a python object containg data in the memory.
Pandas, PySpark, Polars are python external libraries in which dataframe is a core big concept. It is very similar to SQL

###### Why three libraries? why not one?
1. Pandas
- One machine
- Executes Immediately
- Simple

2. Pyspark
- Multiple maachines, data lives mostly in memory
- How it executes the code
It's lazy, nothing gonna run immediately, Pyspark is going to start building our plan step-by-step and start optimizing the entire workflow and only at the end if we request a result, only then 
PySpark can start doing the job and start executing the plan
- Massive data
- Lazy
- Parallel
- Speed
- Complex & Infrastructure

3. Polars
- Simple(One machine)
- Lazy
- Fast
- No INfrastructure
- Small data