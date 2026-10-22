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
few heap pages