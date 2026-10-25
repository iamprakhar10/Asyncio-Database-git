# Notes
It's not a solution for every problem.

Redis is worth learning because it sits exactly between backend engineering, system design, and production AI systems

Redis gives your application a very fast shared storage area, primarily in RAM.

Redis is an in-memory data store supporting key/value access and richer structures such as hashes, sets, sorted sets and streams. One reason it is useful for caching is extremely low access latency.

One feature makes Redis particularly useful: expiration
You can tell Redis:
Store this value, but automatically delete it after 60 seconds.

SET weather:jabalpur {...}

TTL = 60 seconds

User request
   ↓
Nginx
   ↓
FastAPI
   ↓
Authentication
   ↓
Business logic
   ↓
Redis?  ← optional fast layer
   ↓
PostgreSQL ← permanent source of truth

Redis is usually an internal service your backend talks to.
It is not something the client talks to directly.

                    ┌──────── Redis
                    │
User → Nginx → FastAPI
                    │
                    └─ rate-limit check
                         │
                    allowed?
                    /      \
                  no        yes
                  ↓          ↓
                429      Authentication
                              ↓
                        Business logic
                              ↓
                         PostgreSQL

###### Why shouldn't the user connect directly to Redis?
Because Redis is not your public HTTP API.

Redis speaks its own protocol and should normally remain inside your private network                    


One subtle point
The rate limiter doesn't necessarily have to live inside FastAPI.

You could also rate-limit earlier:
User
 ↓
Nginx
 ↓
rate-limit check
 ↓
FastAPI

Nginx itself can perform rate limiting without Redis in simple deployments.

In larger distributed systems, you might instead have:
User
 ↓
API Gateway
 ↓
Rate limiter
 ↓
Redis
 ↓
Backend service




Redis

key                         value

"user:42"              →    "{name: Prakhar, ...}"

"authority:jabalpur"   →    "{...}"

"api_requests:user42"  →    17

A Python dictionary belongs to one Python process.

Redis is a separate process/server, so many application processes can share it.
FastAPI process 1 ──┐
FastAPI process 2 ──┼──► Redis
FastAPI process 3 ──┘

That shared-state aspect becomes very important in production.



###### Where does Redis physically run?
This connects directly to what you've learned about Docker, EC2, processes and networking.

Redis itself is essentially another server process.

For example:
EC2 machine

┌───────────────────────────────┐
│ Linux                         │
│                               │
│ FastAPI process               │
│                               │
│ PostgreSQL process            │
│                               │
│ Redis process                 │
│                               │
└───────────────────────────────┘

Perfectly possible.

Or with Docker:
EC2
│
├── API container
│      FastAPI
│
├── PostgreSQL container
│
└── Redis container


###### What happens in bigger production systems?
You generally don't have to put everything on one EC2 machine.

You could have:
                 Internet
                    │
                    ▼
              Load Balancer
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       API #1               API #2
          │                   │
          └─────────┬─────────┘
                    │
              ┌─────┴─────┐
              ▼           ▼
            Redis      PostgreSQL


###### Why can't we simply use a Python dictionary?
This is a very important system-design question.

Suppose you have:
API process 1

cache = {}

and:
API process 2

cache = {}

These are two separate memories.

Therefore:
Process 1
cache["user:42"] = X

Process 2
cache["user:42"]
              ❌ doesn't exist

With Redis:
          ┌──────── Redis ────────┐
          │                       │
API #1 ───┤                       │
API #2 ───┤  shared data          │
API #3 ───┤                       │
          └───────────────────────┘

Now every process sees the same state.

This is one of the big conceptual reasons Redis appears once applications start scaling horizontally.



docker run -d \
  --name redis-practice \
  -p 127.0.0.1:6379:6379 \
  redis:latest

The official Redis docs recommend Docker as a quick way to run Redis locally. Redis listens on port 6379 by default. Redis

What this means:
Your Mac
│
├── Docker
│    │
│    └── redis-practice container
│          │
│          └── redis-server process
│                 │
│                 └── listens on port 6379
│
└── 127.0.0.1:6379
          │
          └──── forwarded to Redis container


used:
127.0.0.1:6379

instead of:
0.0.0.0:6379

because we're just practicing locally. There's no reason to expose Redis beyond your own machine.
________________________

** docker exec -it redis-practice redis-cli **

At this point, the architecture is:
You
 │
 │ type Redis commands
 ▼
redis-cli
 │
 │ TCP connection
 ▼
Redis server
 │
 ▼
RAM


or
You
 ↓
Terminal
 ↓
redis-cli   ← Redis client program
 ↓
Redis server

Similar to PostgreSQL
You
 ↓
Terminal
 ↓
psql        ← PostgreSQL client
 ↓
PostgreSQL server
______________________

SET name Prakhar

Redis should respond:
OK

Now:
GET name

You should get:
"Prakhar"

Conceptually:
Redis RAM

┌──────────┬───────────┐
│ key      │ value     │
├──────────┼───────────┤
│ name     │ Prakhar   │
└──────────┴───────────┘

_______________________________
EXISTS name

You should get:
(integer) 1

Meaning:
1 = key exists
0 = key does not exist

_______________________________
SET otp 847291
EXPIRE otp 10

>>>TTL otp
7(seconds)

we can also do
SET otp 847291 EX 10

_______________________________
Counters with INCR
Purpose: this is the basis of things like rate limiting, page views, retries and usage counters.

SET requests 0

Then:
INCR requests

Result:
(integer) 1

_______________________________
Rate limiting
SET login_attempts:user42 0 EX 60

This is already very close to how a simple rate limiter works:
Request arrives
      ↓
INCR login_attempts:user42
      ↓
value > 5 ?
   /       \
 yes        no
 ↓           ↓
reject     continue

_________________________________
SET name Prakhar

we were using:
DB 0

automatically.

You can check:
SELECT 1

Now you're using logical database 1.

Then:
GET name

will probably return:
(nil)


Redis logical databases are not comparable to PostgreSQL databases.

They're just numbered namespaces inside the same Redis server.

In real production systems, people often simply use DB 0 and separate things using key names or separate Redis instances/clusters.

#### Redis hashes
Suppose we want to store:
User 42

name = Prakhar
city = Jabalpur
age = 26

We could do:
SET user:42:name Prakhar
SET user:42:city Jabalpur
SET user:42:age 26

But Redis has a more convenient structure called a Hash.
Think:
user:42
   │
   ├── name → Prakhar
   ├── city → Jabalpur
   └── age  → 26

Run:
HSET user:42 name Prakhar city Jabalpur age 26