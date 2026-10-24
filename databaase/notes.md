1. Database + tables
        ↓
2. Basic SQL
        ↓
3. Keys + relationships
        ↓
4. JOINs + aggregations
        ↓
5. Better SQL
        ↓
6. Schema design
        ↓
7. Normalization
        ↓
8. Indexes
        ↓
9. Query plans
        ↓
10. Transactions + ACID
        ↓
11. Concurrency + isolation
        ↓
12. DB internals basics
        ↓
13. Connections + pooling
        ↓
14. Caching
        ↓
15. OLTP vs OLAP
        ↓
16. SQL vs NoSQL
        ↓
17. Replication
        ↓
18. Partitioning + sharding
        ↓
19. Distributed consistency
        ↓
20. Vector databases / RAG storage





#### Indexing(say by email)
The B-tree is made for the index, not for the whole table.
There is no requirement that table rows be sorted by email.

B-TREE INDEX ON email

              root
             /    \
            /      \
       a...m      n...z
        │            │
        ↓            ↓

leaf entries:

a@gmail.com → (page 1, slot 2)
c@gmail.com → (page 2, slot 1)
m@gmail.com → (page 1, slot 3)
z@gmail.com → (page 1, slot 1)


A PostgreSQL data page is typically 8 KB

INDEX IS GREAT WHEN:

"Find a tiny subset of rows"
        ↓
few TIDs
        ↓
few heap pages(heap is not related to heap datastructue)

an index only helps when it meaningfully reduces how much of the table has to be visited.

Indexes can speed up many reads but they make the writes more expensive

Which columns should be usually indexed?
Columns that are frequently used in:
WHERE
JOIN
ORDER BY



Indexes on join columns can make joins significantly faster.
Foreign keys are not automatically indexed in PostgreSQL, which is an important practical detail


###### Composite indexes
Now suppose you frequently run:
SELECT *
FROM complaints
WHERE city = 'Jabalpur'
AND status = 'OPEN';

You could create:
CREATE INDEX idx_city_status
ON complaints(city, status);

This is a composite index because it contains multiple columns.

Conceptually:
(city, status)

Bhopal   CLOSED
Bhopal   OPEN
Indore   CLOSED
Indore   OPEN
Jabalpur CLOSED
Jabalpur OPEN

It is sorted primarily by:
city

and then within a city by:
status

The ordering matters.

#### Transactions
Transfer 34 rs from a to b
a -= 34
b += 34
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE id = 'A';

UPDATE accounts
SET balance = balance + 100
WHERE id = 'B';

COMMIT;
Transaction is basically a boundary:
We are telling database that these operations belong together,
Treat them as one unit

          Transaction
              │
      ┌───────┴───────┐
      ↓               ↓
 subtract A        add B

              ↓

         ALL SUCCEED
             OR
         NONE HAPPEN
If something fails, ROLLBACK



### ACID(Atomicity, Consistency, Isolation, Durability)
##### A — Atomicity
all or nothing
Our bank transfer example.

##### C — Consistency
The database should move:
valid state
    ↓
valid state

For example:
balance cannot violate defined constraints
foreign keys remain valid
unique constraints remain valid

Important nuance: Consistency doesn't mean "every replica instantly has identical data." That's a different meaning of consistency used in distributed systems

##### I - Isolation
It defines how and when changes made by one running transaction become visible to other concurrent transactions.


                    DATABASE
                       │
             ┌─────────┴─────────┐
             │                   │
       Transactions          Concurrency
             │                   │
      group operations      multiple operations
       into one unit          at same time
             │                   │
             └─────────┬─────────┘
                       ↓
                   Isolation
                       ↓
               prevent bad interactions

##### D - Durability
Once:
COMMIT successful

the database promises that the committed change won't simply disappear because the process crashes.




## Concurrency
Multiple requests operating on database arond the same time

We want this behaviour otherwise User B must wait for User A's entire transaction

But concurrency creates problems.
Suppose there is one ticket available and Two peoplebuy simultaneously
             Database
            tickets = 1
             /      \
            /        \
       Request A   Request B
        reads 1     reads 1
            \        /
             \      /
        BOTH THINK THEY
         CAN BUY TICKET

That's a Race condition, therefopre we need isolation/concurrency control





# Caching
Imagine millions of requests ask:

SELECT *
FROM products
WHERE id = 500;

Suppose product 500 barely changes. We would have to process eveyr request via database, even with good index, PostgreSQL has to do the work

We can keep a faster temporary copy.
                  Request
                     ↓
                   Cache
                  /     \
              exists?   missing?
                ↓          ↓
              return    PostgreSQL
                            ↓
                       put into cache
                            ↓
                          return


The cache stores a copy of some data/result.

For example:
Redis

key:
product:500

value:
{
   name: MacBook,
   price: 100000
}                          
----------------------------
Then:
GET product:500

can be extremely fast
----------------------------
Why cache is faster?
- cache often keeps hot data in RAM
- Simpler Lookup
- avoids joins/caculations
- reduces load on the primary database


###### But caching creates a new problem
PostgreSQL:
price = ₹90,000

Redis cache:
price = ₹100,000

Once I have two copies of data, how do I keep them consistent enough?
 
Caching invalidation
One strategy:
UPDATE database
then
DELETE cached product:500

Next request:
cache miss
    ↓
DB
    ↓
₹90,000
    ↓
put ₹90,000 into cache


TTL (Time to live)
Another solution:
Keep cached value only for a certain amount of time.





# Database Connectiosn and Connection pooling

Why do we need connections at all?
Our FastAPI Application and PostgreSQL are sepateate programs, often separate processes and sometines separate machines

When we do this(below code)

db.query(User).filter(User.id == 5).first()


conceptually this has to happen:
FastAPI process
      |
      |  database connection
      v
PostgreSQL server
      |
      | executes SQL
      v
returns rows

A database connection is a long lived communication session between our application and DB server

It's not just:
send SQL packet
receive answer
done

FastAPI process
    |
    | database connection
    |  (usually TCP socket)
    v
PostgreSQL server

connection ≠ process

one active DB connection
        ↕
one PostgreSQL backend process

500 HTTP requests
       |
       v
FastAPI
       |
   connection pool
   [C1 C2 C3 ... C20]
       |
       v
~20 PostgreSQL backend processes

a connection is handled by a PostgreSQL backend process, but the connection itself is not that process, in normal PostgreSQL architecture, one client connection is handled by one dedicated PostgreSQL backend process

There is also a main PostgreSQL server process plus background processes for things like checkpoints, WAL, autovacuum, etc., so PostgreSQL as a whole is not just those 20 processes


Also PostgreSQL cannot comfortably accept an unlimited number of active connections. Every DB connection consumes memory and other resources.

So instead:
                 CONNECTION POOL

FastAPI      ┌──────────────────────┐
requests --->│ connection 1         │
             │ connection 2         │
             │ connection 3         │
             │ connection 4         │
             └──────────┬───────────┘
                        |
                        v
                   PostgreSQL

The connections are created ahead of time or reused.
What happens during a request?
Suppose your pool has 5 connections.
Pool:

C1  free
C2  free
C3  busy
C4  free
C5  busy

New request comes in:
request
   |
   v
borrow C1
   |
run SQL
   |
receive result
   |
return C1 to pool

The connection is not destroyed.

It goes back into the pool.

That's connection pooling.



## Replication
Maintaining copies of same database on multiple servers

                 Primary
                PostgreSQL
                    |
          replication stream
          /         |         \
         v          v          v
      Replica 1  Replica 2  Replica 3

Why replicate?
Suppose:
writes = 1,000/sec
reads  = 100,000/sec

Instead of making one machine do everything:
                Primary
                  |
            writes happen here
                  |
        +---------+---------+
        |         |         |
        v         v         v
     Replica   Replica   Replica
       reads     reads     reads    


Replication lag

WRITE
  |
  v
Primary
  |
  v
success

then immediately

READ
  |
  v
Replica

may return stale data.       



## Failover
Replication isn't only about scaling reads.

Suppose your primary dies:
                 Primary
                   X
                crashed

                  |
         +--------+--------+
         |                 |
         v                 v
      Replica A         Replica B

One replica can be promoted:
Replica A
   |
   v
NEW PRIMARY

Applications reconnect to it.

Replicating Reads won't help if the bottleneck becomes write operation. If that happens, we have to consider Sharding



Resharding
Suppose you originally had:
4 shards

then need:
8 shards

Now huge amounts of data may need to move.
old shard
   |
   | move rows
   v
new shards

while the system remains online.

That is hard.

So sharding is generally something you avoid until you actually need it.


# Distributed database Theory

Question: Waht happens whne one logical database is spread across multiple machines connected by a network

Answer: A lot of assumptions we had with one machine stop being true

Every time you add another database machine, you gain capacity or reliability, but you also create coordination problems.

CAP Theorem: 

C - Consistency
A - Availability
P - Partition Tolerance

For a distributed system, the theorem states that it is possible  to attain only two properies and the third would be always compromised

The system requirements should define which two properties should be chosen over the rest

CA - Monolithic(One server serves everything, so it will be consistent and Available)
AP - Loose consistency(Social media posts)
CP - Loose availability(Bank server on updates)


Generally choice comes down to C or A. Partition tolerance should always be there

Blog website - A
Multiplayer online game - A
stock trading platforms - C
video streaming sites - A
Ticket booking systems - C
Video chat applications - A
Bank - C

Across machines
Now:
Node A
   |
   | network
   |
Node B
   |
   | network
   |
Node C

The network can:
be slow
drop packets
partition
reorder/delay messages


What if A and B are working but they simply can't communicate.
That's network Partition

Strong consistency
Eventual Consistency
Quorums

Atomicity becomes much harder when multiple independent machines participate.


In a FastAPI + SQLAlchemy app, you usually do something more like this:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(    
        bind=engine,    
        autoflush=False,    
        autocommit=False,)


The important part is:
engine = create_engine(DATABASE_URL)


The engine is the main SQLAlchemy object that knows:
- how to connect to PostgreSQL
- what driver to use
- how to manage the connection pool



### Our Public pulse app flow

Session and connection are different
In your app, the connection is that real wire-level link to PostgreSQL. The session is the SQLAlchemy object you use in your code to talk to the DB. It's like a wrapper, almost like a “work session.” The session will grab a connection from the pool only when it actually needs to run SQL. And then when you close()

How do we configure the engine's pool

You pass pool settings to create_engine(). For example, pool size, max overflow, pool timeout, pool recycle, pool pre ping. You do it once when the app starts. The pool then lives inside the engine, and sessions borrow connections from it. A common pattern is pool size maybe like 5 to 20, small overflow, and pool_pre_ping=True to avoid stale connections. If you want, I can show a concrete config for your FastAPI project.


# Types of database
Verical scaling is poor in SQL databases
## Key Value stores
NoSQL database
(Redis, DynamoDB, Memchached): one key in, one value out 

A Key-Value Store is a type of NoSQL database that uses a simple data model: data is stored as a collection of key-value pairs, where every single item is accessed via a unique identifier (the key).

Coat check: Hand over the ticket, get the coat. But we can't find 
"All the coats that are black"
Limited searchability and filtering

How it works - 
The Key: A unique string or identifier (e.g., user:1005:session, product_price_452). Keys must be unique within the database.

The Value: Can be anything—a simple string, a JSON object, a binary blob, an image, or a serialized data structure. The database engine generally doesn't care what is inside the value; it just treats it as a chunk of data attached to that key.

###### advantages
Blazing Fast Performance (O(1) Complexity): Because lookups are done via hashing algorithms rather than complex table scans or multi-table joins, finding and fetching data takes constant time, making operations ultra-fast.

High Scalability: They are architected to scale horizontally easily (sharding data across multiple servers), making them ideal for massive web-scale applications.

Flexible Schema (Schemaless): Unlike relational databases (SQL), you don't need to define columns or data types beforehand. Different keys can hold completely different structures of values

###### disadvantages

Limited searchability and filtering. Only finadable by key

Data duplication and consistency challanges - Because there are no foreign keys or relational constraints, applications often duplicate data across multiple keys to optimize for read speed. If that underlying data changes, your application must manually update every single key where it was duplicated, increasing the risk of data inconsistency

Lack of standard quering language





## Document Databases
Data is stored ad JSON-style documents. One document holds the whole object,
including nested arrays and sub-objects

While postgreSQL will use our models to store data, a document database might store one product(say e-commerce) as

{
  "_id": 123,
  "name": "Laptop",
  "brand": "ABC",
  "specs": {
    "ram": "16GB",
    "storage": "1TB",
    "cpu": "M4"
  },
  "tags": ["laptop", "electronics"],
  "reviews": [
    {
      "rating": 5,
      "comment": "Great laptop"
    },
    {
      "rating": 4,
      "comment": "Good battery"
    }
  ]
}

*Question* - What is the need of these things?
Because sometimes the natural shape of your data is already:
one thing
  ├── nested properties
  ├── arrays
  ├── optional fields
  └── sub-objects

and you usually read that whole thing together.

For example:
product
user profile
blog post
CMS page
configuration object
IoT device record
event payload

For these, splitting everything into normalized relational tables can sometimes feel unnecessary

In a relational DB, rows in a table generally share the same columns.

In MongoDB, two documents in the same collection can look different

PostgreSQL        MongoDB
──────────        ───────
table             collection
row               document
column            field

Why not just use PostgreSQL JSON?
Very good question.

PostgreSQL supports:
JSONB

so you can absolutely store flexible JSON-like data there too.

That's why nowadays the decision isn't:
"JSON data → MongoDB."

It's more:
"Is the application naturally document-oriented enough that a document database gives us simpler modeling and access patterns?"

For many systems, PostgreSQL + JSONB is enough

When would I choose MongoDB?
I'd seriously consider it if most of these are true:
- data naturally looks like nested JSON documents
- documents are mostly accessed independently
- schema varies significantly between records
- you frequently retrieve most of a document together
- relationships between documents are limited
- flexible schema provides real value
I'd lean PostgreSQL if:
- data is highly relational
- joins are common
- transactions are important
- constraints are important
- correctness across multiple entities matters
- SQL analytics/querying is important
The best mental model is:
Relational databases organize around relationships between entities. Document databases organize around self-contained aggregates/documents.


Document database search
In a document database like MongoDB, searching works very similarly in spirit to PostgreSQL:
If there is no useful index, MongoDB may scan many documents.
If there is an index, it uses that index to quickly find matching documents
Query
  ↓
Does useful index exist?
  ↓
YES ──→ search index → fetch matching documents

NO ───→ scan documents


for ordinary document-field lookup, think: B-tree-style index over document fields
###### Disadvantages
Data duplication