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

So the data which is already present in RAM, which is used by Pandas, looks different when it's used in Spark, and that conversion is done by Arrow
Yes, exactly. You've understood the main idea. There is just one technical correction: Arrow doesn't perform every conversion automatically. It defines a standardized in-memory representation, and libraries such as PyArrow implement the conversion.

The same logical data can have different physical representations in RAM.

For example, consider three ages: 25, 30, 35.

Spark: Typically represents the data using its JVM-based internal structures, often optimized for distributed and columnar processing.

Pandas: Represents the data using structures such as NumPy arrays or Arrow-backed arrays.

Arrow: Defines a standard columnar memory layout that allows the two environments to exchange data efficiently.