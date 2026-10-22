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

