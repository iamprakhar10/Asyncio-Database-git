# RAG

#### Why basic RAG is not Enough
Query: What is the refund policy for SKU XJ-4821?

Semantic embeddings aren't necessarily the best mechanism for matching exact product IDs.

Keyword search is excellent at it.


###### Problem 1-> Semantic similarity is not always Relevance

That's why production RAG often combines:
Dense retrieval
       +
Sparse retrieval

###### Problem 2 -> The chunk containing the answer isn't necessarily similar to the question(which basic RAG depends on)

Suppose a company document says:
================================
AWS Deployment Manual
================================

Section 1
EC2 configuration...

Section 2
Security...

Section 3
Database backups...

Backups are retained for 14 days.

Section 4
Monitoring...

Your query:
"How long are database backups kept?"

The relevant chunk:
Backups are retained for 14 days.

is tiny.

Its embedding might not contain much context.

Compare:
Database backup policy:
Production PostgreSQL backups are retained for 14 days.

That representation is much easier to retrieve.

This motivates things like:
- contextual chunking
- document-title augmentation
- parent-child retrieval
- richer metadata
Chunking is therefore part of retrieval, not merely preprocessing.


###### Problem 3->One Query may actually contain several questions

Query: How does the refund policy of the Enterprise plan
compare with the Business plan?

To answer this we need:
Query A:
Enterprise refund policy

Query B:
Business refund policy

Then:
retrieve(A)
retrieve(B)

        ↓

combine evidence

        ↓

answer comparison

Embedding the entire original query once may retrieve mainly Enterprise documents or mainly Business documents.

This leads us to query decomposition

###### Problem 4 -> User Language and document language may differ

User:
How do I stop paying?

Documentation:
Subscription cancellation procedure

An embedding model may bridge this gap, but not always.

We could first transform:
"How do I stop paying?"

into:
"How can a user cancel their subscription
and terminate recurring billing?"

Then retrieve.

That is query rewriting.

###### Problem 5 -> Retrieval has two competing goals

             RETRIEVER
         optimize for recall

Query → retrieve ~30–100 candidates

                 ↓

              RERANKER
         optimize for precision

                 ↓

              top ~5–10


###### Problem 6 -> More context can make RAG worse              
Good retrieval is about:
giving the LLM the smallest amount of evidence that is sufficient to answer correctly.






## Hybrid Search
##### Dense retrieval vs sparse retrieval

Dense retrieval is our absic embedding baseed retrieval

Sparse retrieval works differently.
It focuses much more on the actual words/tokens appearing in the query and document.

A common sparse retrieval algorithm is:
BM25 - A smarter version of keyword matching.

It asks three main questions:
1. Does the word appear in this document?
2. Is this word rare across the whole document collection?
3. How many times does it appear in this document?


So BM25 gives rare terms much more importance.("E-104" will be more important than "the")

Architecture:
                       Query
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
     Dense Retrieval              BM25 Search
            │                         │
       semantic ranking          lexical ranking
            │                         │
            └────────────┬────────────┘
                         ▼
                     Fusion
                         │
                         ▼
                Final candidate list

______________________________________________________


                    Query
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Vector search              BM25
       Top 30                  Top 30
          │                       │
          └───────────┬───────────┘
                      ▼
                     RRF
                      │
                   Top 30
                      │
                      ▼
                 Reranker
                      │
                    Top 5
                      │
                      ▼
                     LLM

Hybrid retrieval does not replace reranking.                     

###  BM 25
Lets start from Ground up so the formula doesn't feel arbitrary

###### Start with plain keyword counting 
Suppose the query is:
authentication token

And we have:
D1: authentication token expired
D2: authentication authentication authentication guide
D3: password reset guide

The simplest possible scoring method is:
score = number of query-term matches

Then:
D1 → 2 matches
D2 → 3 matches
D3 → 0

This would rank D2 above D1.

But D1 is probably more useful because it contains both important terms.

So raw counts are too crude.

###### Term Frequency: TF
TF asks:
How often does this term appear in this document?

For term t and document d:

TF(t,d) = count of  t  in  d

Example:
D1: authentication token expired

For "authentication":

TF = 1

For:
D2: authentication authentication authentication guide


TF = 3

So repeated occurrences increase relevance.

That makes sense.

But here's the problem:
authentication
authentication authentication
authentication authentication authentication

Should the third repetition really make the document 3× more relevant than the first?

Usually, no.

This will matter later in BM25.

###### IDF: rare terms should matter more
Suppose our corpus has 1,000,000 documents.

The term:
user

appears in:
800,000 documents

while:
E104

appears in:
20 documents

If the query is:
user E104

which term is more useful?

Clearly:
E104

because it dramatically narrows the search.

That is the idea behind:
Inverse Document Frequency

IDF(t) = log(N / {df(t)})

Where
N     = total number of documents
df(t) = number of documents containing term t

###### 4. TF-IDF
Now combine the two ideas:

TFIDF(t,d) = TF(t,d) * IDF(t)
ALMOST -> Frequency in a particular document * Rarity across all documents
For an entire query, sum over the query terms:

score(d,q) = sum_[t in q]{TF(t,d)* IDF(t)}

*it is almost entirely pre-computed before you ever run a query.*