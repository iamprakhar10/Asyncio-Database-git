# Query Tansformation
The problem it solves :-
Even with perfect documents and perfect chunking, the user's query itself may be a poor search query

1. Query rewriting — turn a vague/user-style question into a better retrieval query.
2. Multi-query retrieval — generate several versions of the question and retrieve for all of them.
3. HyDE — generate a hypothetical answer/document first, then retrieve using its embedding.
4. Step-back prompting — retrieve using a more general version of the question.
5. Query decomposition — split a complex question into multiple subqueries.

##### Why is this needed if embeddings understand meaning?
Because embeddings aren't magic.

Queries can contain:
vague language
pronouns
missing terminology
multiple questions
ambiguous wording
too much irrelevant text
user-specific phrasing

### Query rewriting
This is the simplest.

User:
How do I stop paying?

Rewrite:
How can a customer cancel a recurring subscription
and stop future billing?

Then retrieve with the rewritten query.

The goal is not to answer the question.

The goal is to make the query better for search.
Where does the rewrite come from?
Usually one of:
LLM
rules/templates
search-query model

For flexible natural language, an LLM is common.

That means yes, potentially an extra LLM call before retrieval:
User query
    ↓
LLM rewrite
    ↓
retrieval
    ↓
LLM final answer

So potentially two LLM calls.

But again, query rewriting is optional. If your original queries already retrieve well, don't add it.

##### Query rewriting can also remove conversational noise
Suppose the conversation is:
User:
Tell me about the Enterprise plan.

Assistant:
...

User:
What about refunds?

The literal query:
What about refunds?

is terrible on its own.

A rewrite using conversation history could produce:
What is the refund policy for the Enterprise plan?

This is a very important production use case.

It's often called:
standalone question generation

or conversational query rewriting.

So:
conversation history
+
latest user message
        ↓
rewrite
        ↓
standalone retrieval query



### Multi-query retrieval
Sometimes there isn't one obviously best rewrite.

Suppose:
How does authentication state persist after the access token expires?

We could search:
access token expiration refresh token

or:
authentication session after JWT expiration

or:
renew access token using refresh token

Different formulations may retrieve different useful chunks.

So generate multiple queries:
Q1
Q2
Q3

and run retrieval for each:
                Original question
                       ↓
                 Generate queries
                /       |        \
              Q1        Q2        Q3
              ↓         ↓         ↓
          retrieve   retrieve   retrieve
                \       |       /
                 merge results
                       ↓
                  deduplicate
                       ↓
                    reranker

This improves retrieval recall.

If one phrasing fails, another might succeed.
But it costs more
Suppose one vector search costs X.

Three queries means roughly:
3 query embeddings
3 searches
more candidates
more reranking

So multi-query retrieval trades:
more recall
for
more latency/cost

You should evaluate whether it helps enough.


### HyDE
This one is more unusual.

HyDE means:

Hypothetical Document Embeddings

Instead of embedding the user's short question directly, ask an LLM to generate a hypothetical answer/document.

User asks:
Why does error E104 occur?

The LLM generates something like:
Error E104 occurs when an authentication token has expired.
The user must obtain or refresh the token before retrying.

We do not trust this as the answer.

Instead:
hypothetical answer
        ↓
embedding
        ↓
vector search

Why might this work?

Because documents in your knowledge base often look more like answers than like questions.

Compare:
Query:
Why does E104 occur?

with stored document:
E104 occurs when the authentication token has expired.

The generated hypothetical document may sit closer in embedding space to the real document.

Then we retrieve real evidence and answer from that.

The key rule:
HyDE-generated text is used for retrieval, not treated as factual evidence



### Step-back querying
Sometimes the user's question is too specific.

Example:
Why does our FastAPI endpoint return 401
after the access token expires?

A step-back query asks the broader underlying concept:
How does access-token expiration and refresh-token
authentication work?

Retrieve broader explanatory material, then use it to answer the specific question.

So:
specific question
      ↓
broader conceptual query
      ↓
retrieve background knowledge

This is useful when solving the specific query requires understanding a more general concept.



### Query decomposition
This is the most important one for complex questions.

Suppose:
Compare the Enterprise and Business refund policies
and tell me which one allows a longer refund period.

That really contains:
Q1:
What is the Enterprise refund period?

Q2:
What is the Business refund period?

Retrieve separately:
Q1 → Enterprise evidence
Q2 → Business evidence

Then combine:
Enterprise = 30 days
Business = 14 days
        ↓
comparison
        ↓
Enterprise is longer

One giant embedding of the original question might retrieve mostly one side.

Decomposition ensures each information need gets searched.

This becomes especially important for multi-hop RAG, which we'll study later.


## Should every RAG system use all five?
Absolutely not.

A production system might use only:
conversational rewrite
+
decomposition for complex questions

and nothing else.

The correct process is:
baseline retrieval
    ↓
evaluate failures
    ↓
identify query-side failure
    ↓
add appropriate transformation

For example:
pronouns / chat history problem
→ rewriting

different phrasings miss evidence
→ multi-query

query-to-document semantic mismatch
→ HyDE

specific question lacks broad context
→ step-back

question contains multiple information needs
→ decomposition













## Query Rewriting
This is the simplest.

Suppose the user asks:
How do I stop paying every month?

Your documentation says:
Recurring subscriptions may be cancelled from
the billing settings page.

The user's words and document words differ considerably.

A rewrite might be:
How can a customer cancel a recurring subscription
and stop future recurring billing?

Then you search with the rewritten version.
What changed?
The meaning did not intentionally change.

We simply converted:
casual user language
        ↓
retrieval-friendly language

That's query rewriting.
A particularly important use: conversational RAG
Suppose:
User:
Tell me about the Enterprise plan.

Assistant:
...

User:
How long are refunds allowed?

The latest message:
How long are refunds allowed?

doesn't contain "Enterprise".

If you search only that sentence, you could retrieve refund policies for every product.

So the system uses the recent conversation and rewrites it:
What is the refund period for the Enterprise plan?

Now it is a standalone query, meaning:
A question that contains enough information to be understood without needing the previous conversation.

So if you hear:
standalone question generation

it simply means turning:
"What about refunds?"

into:
"What is the Enterprise Plan refund policy?"

using conversation history.
How is rewriting actually done?
Often with an LLM.

Conceptually you give it:
Conversation:
User: Tell me about Enterprise...
Assistant: ...

Latest question:
"What about refunds?"

Task:
Rewrite the latest question as a standalone search query.
Do not answer it.

Output:
What is the Enterprise Plan refund policy?

Then that goes into retrieval.

So yes, this can add an extra LLM call:
LLM #1 → rewrite query
retrieval
LLM #2 → answer using retrieved evidence

But it doesn't have to.

Simple transformations can also be deterministic.

For example:
"docs after:2025 product:enterprise refunds"

could be parsed using rules.

But flexible natural-language rewriting is usually where an LLM is useful.
Should we discard the original query?
Not necessarily.

This is an important detail.

Suppose user asks:
E104 after OAuth callback

LLM rewrites:
Authentication failure occurring after an OAuth callback.

The rewrite has accidentally removed the exact token:
E104

BM25 would have loved that token.

So a robust approach can search using both:
Original:
"E104 after OAuth callback"

Rewritten:
"Authentication error E104 occurring after an OAuth callback"

Or simply instruct the rewrite model:
Preserve exact identifiers, error codes, names, versions, numbers and technical terms.

Query rewriting can hurt if it throws away important lexical information.
Query rewriting can also simplify noisy queries
Suppose:
Okay so yesterday I was working on this and I'm not entirely
sure what happened but basically after I logged in again it seems
like the token wasn't working, so can you tell me what happens
when an access token expires?

Search query could simply become:
What happens when an access token expires?

The transformation removes irrelevant conversational material.