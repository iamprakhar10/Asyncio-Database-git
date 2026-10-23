##### Signed URLs
In our public pulse we didn't used signed URLs. For the Pricvate S3 backup bucket, the EC2 accessed S3 using AWS credentials from it's IAM role, not through presigned/signed URL

A signed URL is basically:
A normal URL plus cryptographic proof saying, “whoever has this URL is allowed to perform this specific action for a limited time.”

For example, imagine this S3 object is private:
s3://my-private-bucket/report.pdf

Normally, if someone opens:
https://my-private-bucket.s3.amazonaws.com/report.pdf

AWS says:
Access Denied

because the object is private.

But your backend can generate a presigned URL like:
https://my-private-bucket.s3.amazonaws.com/report.pdf
    ?X-Amz-Expires=900
    &X-Amz-Signature=abc123...
    &...

That URL might mean:
Permission:
GET this specific object

Valid for:
15 minutes

Authenticated by:
cryptographic signature

So AWS can verify:
Incoming request
      ↓
Which object?
      ↓
Which HTTP action?  GET / PUT?
      ↓
Has URL expired?
      ↓
Is signature valid?
      ↓
YES
      ↓
Allow access

The main problem it solves is this:

Suppose your user needs to download a private file.

Without signed URLs, you might do:
User
  ↓
Your FastAPI server
  ↓
FastAPI downloads file from S3
  ↓
FastAPI sends file to user

That means your server becomes a middleman for potentially huge files.
It will also avoid us giving our AWS credentials to users

Backend has AWS permission
        ↓
creates temporary signed URL
        ↓
frontend gets only temporary permission


The signature is important because without it, someone could simply change:
/report-123.pdf

to:
/report-999.pdf

Backend has AWS credentials
        ↓
Backend creates a signature from:

HTTP method
object path
expiry time
timestamp
credential identity
other request details
        ↓
Backend puts that signature into the URL
So a presigned URL is basically self-contained temporary authorization. S3 doesn't need to store a separate “this URL was issued” record beforehand.




##### Cache eviction policyu
Here are the other main cache eviction policies used in systems like Redis, operating systems, and CPU caches:

0. LRU
LRU = Least Recently Used.

1. LFU (Least Frequently Used)
How it works: Tracks how many times an item has been accessed. If the cache is full, it evicts the item with the lowest hit count.

Best for: Scenarios where certain items are consistently popular over a long period (e.g., a trending product page or popular configuration file).

2. FIFO (First-In, First-Out)
How it works: Evicts the oldest item that entered the cache, regardless of how often or recently it was accessed.

Best for: Simple, low-overhead queues where older data naturally becomes obsolete quickly.

3. MRU (Most Recently Used)
How it works: Evicts the most recently used items first (the exact opposite of LRU).

Best for: Cyclic or repeating data access patterns where older data is actually more likely to be needed again soon than brand-new data.

4. Random Replacement (RR)
How it works: Picks a completely random item to kick out when space runs out.

Best for: Extremely high-performance systems where tracking usage metadata (like timestamps or access counters) adds too much CPU or memory overhead.

5. TTL (Time-To-Live) / Expiration
How it works: Items are automatically evicted after a set amount of time (e.g., 60 seconds), regardless of whether they were recently used or how frequently.

Best for: Caching time-sensitive data like stock prices, weather updates, or session tokens.



There is another cost: caching makes the system more complex because now you have to worry about stale data and invalidation


##### CDN
A CDN is a Content Delivery Network.

The key idea is:
Put copies of content on servers geographically closer to users.

It solves several problems at once
1 - Latency
2 - Less origin load(With many edge servesrs, origin seees only some requests)
3 -  Better Scalibility(Statis content can be served from many distributed locations)


Caching Static Content: It stores static files so the origin server doesn't have to repeatedly serve the exact same image or script to thousands of different people.

Offloading Traffic: By handling requests at the edge, your main origin server experiences significantly less load and doesn't need to scale as massively to handle traffic spikes.

Security and DDoS Protection: Because all incoming traffic hits the CDN's edge servers first before reaching your actual infrastructure, CDNs act as a protective shield. They can absorb massive DDoS attacks, block malicious IPs, and handle SSL/TLS certificates.

Dynamic Acceleration: Advanced CDNs don't just cache static files; they can also optimize the network route back to your origin server for dynamic API requests (like database queries



Frontend
   │
   │ POST /movies/123/play
   ▼
API server
   │
   │ returns CDN URL
   ▼
Frontend
   │
   │ GET video chunks
   ▼
CDN edge

you could have:
https://api.example.com/movies/123

for metadata, while the actual video comes from:
https://video.example.com/movies/123/segment001.ts
https://video.example.com/movies/123/segment002.ts
https://video.example.com/movies/123/segment003.ts