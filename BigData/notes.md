# Big Data
Big Data is not a programming language, software, or framework. It is a category of problems involving data that is difficult to store, process, or analyze efficiently using conventional approaches.

Apache Spark, Databricks, Kafka, Hadoop, and other technologies are different solutions to problems that arise when working with data at scale.

The most important thing is to understand why these technologies exist and how they fit together, rather than memorizing their names.


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