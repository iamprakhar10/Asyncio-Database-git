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


## Multi-query retrieval
Query rewriting assumes:
There is one good search formulation.

Sometimes that's not true.

Consider:
How does the application maintain authentication
after the access token expires?

Useful documentation might use very different terminology.

One document:
Refresh token flow

Another:
JWT renewal

Another:
Session continuation after token expiry

So instead of generating one rewritten query, generate several:
Q1:
access token expiration refresh token flow

Q2:
JWT renewal after token expiry

Q3:
maintaining authenticated session after access token expiration

Then run retrieval separately:
                         Query
                           ↓
                  generate alternatives
                     /      |      \
                   Q1       Q2      Q3
                   ↓        ↓       ↓
               retrieve  retrieve retrieve
                     \      |      /
                       merge
                         ↓
                     deduplicate
                         ↓
                       rerank

What is deduplication?
If Q1 and Q2 both retrieve the same chunk, you don't want two copies.

So:
Q1 → D7, D9, D3
Q2 → D7, D4, D8

after deduplication:
D7, D9, D3, D4, D8

D7 appears once.

Then the reranker can judge them all against the user's original information need.
#### What problem does multi-query solve?
Primarily recall.

Remember:
Recall asks whether we managed to retrieve the relevant evidence at all.

Different query wording explores different parts of the retrieval space.

If:
Q1 misses the answer

perhaps:
Q2 retrieves it.

#### What is the downside?
Cost and latency.

Three queries can mean:
3 query generations
3 embeddings
3 vector searches
possibly 3 BM25 searches
larger candidate set
more reranking work

So you don't blindly generate 20 queries.

Often a small number such as 2–5 alternatives is enough to experiment with.

The correct number should come from evaluation.
#### Multi-query vs ordinary query expansion
You may hear query expansion.

This broadly means adding related terms or concepts to make search broader.

For example:
Original:
"JWT expiry"

Expanded:
"JWT expiry access token expiration token renewal refresh token"

Multi-query retrieval instead creates separate queries:
JWT token expiration
refresh-token renewal
authentication after token expiry

The concepts overlap, but the implementation differs:
query expansion
→ one richer query

multi-query
→ several separate searches

- - - - - - - - - - - - - - - - - - - - - - - - - - - - 
Just like with hybrid search, you cannot simply add or average the raw scores from these different query variants because vector spaces and distance metrics shift depending on how a sentence is phrased.

To merge these multi-query lists cleanly, systems rely on Reciprocal Rank Fusion (RRF) adapted for multi-query aggregation.

Once RRF merges the multi-query lists into a single, deduplicated candidate pool (e.g., the top 30 documents), that pool is handed off to the Cross-Encoder Re-ranker we discussed earlier to perform deep textual cross-attention against the original user prompt and pick the final 3 to 5 chunks for the LLM.
- - - - - - - - - - - - - - - - - - - - - - - - - - - -  



## HyDE
Hypothetical document embeddings

Suppose user asks:
Why does error E104 occur?

A question is short:
Why does error E104 occur?

But your knowledge base consists of answer-like passages:
Error E104 occurs when the authentication token has expired.
Generate a fresh token and retry the request.

The idea behind HyDE is:
Ask an LLM to imagine what a useful answer passage might look like, then embed that passage and use it to search for real documents.

So:
User query:
"Why does error E104 occur?"
        ↓
LLM creates hypothetical passage
        ↓
"Error E104 occurs when an authentication token
expires and must be renewed..."
        ↓
embed hypothetical passage
        ↓
vector search
        ↓
real documents

#### Wait—isn't the LLM hallucinating?
Potentially, yes.

And that is okay only because the hypothetical text is not treated as evidence.

Suppose it incorrectly generates:
E104 occurs because the database connection expires.

We do not answer the user with that.

We use its embedding as a search probe.

Then the actual retrieval might find:
E104 occurs when the authentication token expires.

The final answer must come from real retrieved documents.

So:
HyDE output
→ retrieval tool

NOT
→ factual source

This distinction is essential.
#### Why can HyDE work?
Embedding models often compare texts more effectively when the texts have similar styles and semantic density.

Compare:
Question:
Why does E104 occur?

against:
Document:
E104 occurs when...

versus comparing:
Hypothetical explanatory paragraph

against:
Real explanatory paragraph

The second pair may occupy more similar regions in embedding space.
#### Does HyDE help BM25?
Not primarily.

HyDE was designed around dense embeddings.

You could technically use generated text for lexical retrieval too, but its main motivation is improving dense semantic retrieval.
#### Cost
Again, you need an LLM before retrieval:
LLM → hypothetical document
retrieval
LLM → final answer

So don't add it unless evaluation shows it improves retrieval.


## Step-back querying
Now suppose the user's question is very specific:
Why does my FastAPI endpoint return 401 immediately
after an access token expires?

Perhaps the knowledge base doesn't contain that exact question.

But it contains broader material:
JWT access-token expiration and refresh-token authentication

A step-back query deliberately asks a broader question:
How does access-token expiration and refresh-token
authentication work?

So:
Specific query
      ↓
step back to broader underlying concept
      ↓
retrieve conceptual background

Then use that background to help answer the specific question.
#### Why would broadening help?
Because sometimes the answer requires a concept rather than a direct sentence match.

Imagine asking:
Why does PostgreSQL index lookup sometimes still require
reading the heap page?

A broader query might be:
How do PostgreSQL B-tree indexes reference heap tuples?

That may retrieve the underlying explanation needed to answer the specific question.
#### Step-back is different from rewriting
Rewrite:
"Why am I getting 401?"
        ↓
"Why does an expired access token cause HTTP 401?"

Same level of specificity.

Step-back:
"Why does an expired access token cause HTTP 401?"
        ↓
"How does token-based authentication and expiration work?"

It intentionally moves to a more general concept.

Sometimes systems retrieve using both:
specific query
+
step-back query

Then combine the evidence.

That is often safer than replacing the original query entirely.

## Query decomposition
This is probably the most important advanced technique when questions become complex.

Suppose:
Compare the Enterprise and Business refund policies
and tell me which gives customers more time.

This is not really one information need.

It contains:
Need A:
Enterprise refund period

Need B:
Business refund period

Then:
compare A and B

If you embed the original long question once, retrieval might strongly retrieve Enterprise docs but miss Business docs.

So we decompose:
Original
   ↓
Subquery 1:
What is the Enterprise Plan refund period?

Subquery 2:
What is the Business Plan refund period?

Retrieve each separately:
Q1 → Enterprise evidence → 30 days
Q2 → Business evidence   → 14 days

Then the final model compares:
30 > 14

and answers.
#### Another decomposition example
Question:
Was the refund policy changed after the Enterprise
Plan price increased?

To answer properly you might need:
What was the old Enterprise refund policy?

What is the current Enterprise refund policy?

When did the Enterprise price change?

Then combine those facts.

This is where RAG starts moving toward multi-hop retrieval.
#### What is multi-hop retrieval?
It simply means:
Answering the question requires retrieving multiple pieces of evidence, sometimes where one retrieved fact determines what you search for next.

Example:
Question:
Who became CEO after the company that acquired Acme
changed leadership?

You might first need:
Who acquired Acme?

Result:
Company X

Then search:
Who became CEO of Company X?

The second retrieval depends on the first retrieval result.

That's a true multi-hop process.

We'll study that separately later.

Simple query decomposition does not necessarily require sequential dependencies. You can often run all subqueries in parallel.
#### Who performs decomposition?
Often an LLM.

You give it:
Question:
Compare Enterprise and Business refund policies...

and ask for structured output:
{    "subqueries": [        "What is the Enterprise refund period?",        "What is the Business refund period?"    ]}


Then your application executes those searches.

Again:
LLM decomposition call
→ retrieval calls
→ final answer LLM

Potential extra LLM cost.




# new heading
### Metadata and query transformation can work together
Suppose user says:
Compare the 2026 Enterprise and Business refund periods.

A query-understanding step might produce:
Subquery 1:
refund period
filter:
product = enterprise
year = 2026

Subquery 2:
refund period
filter:
product = business
year = 2026

Where did those metadata fields come from?

The metadata schema was designed during ingestion and stored on chunks. product and year values might have come from the source database/application, file path, parser, user input, or another extraction step depending on the project.

At query time, the parser/LLM is merely generating filter conditions against fields we already know exist.

So transformation and metadata filtering complement each other:
query transformation
→ what should I search for?

metadata filters
→ where am I allowed / supposed to search?

### How does the system decide whether transformation is needed?
There are several approaches.

A simple system may always rewrite queries.

A slightly smarter system might use deterministic checks:
Does query contain pronouns like "that", "it", "those"?
Does it reference prior conversation?
Does it contain "compare", "and", "versus"?

A more flexible system can ask an LLM/classifier:
Does this query require:
- direct retrieval
- rewrite
- decomposition
- multiple searches?

Once you start dynamically deciding this, you move toward routing or agentic retrieval, which we'll cover later.

### Do real systems use every transformation?
No.

This is critical.

A bad engineering mindset would be:
rewrite
→ multi-query
→ HyDE
→ step-back
→ decomposition

for every query.

That's absurdly expensive and can actually reduce quality.

Instead:
simple question
→ direct retrieval

ambiguous conversational question
→ rewrite

complex comparison
→ decomposition

retrieval recall problem
→ perhaps multi-query

special semantic mismatch
→ experiment with HyDE

Advanced RAG means selectively solving measured failure modes, not stacking every technique.



# Multi-hop retrieval
The core idea is simple:
A question is multi-hop when answering it requires multiple pieces of evidence, and at least one retrieval step may depend on information discovered in an earlier step.

That last part is what makes it different from ordinary query decomposition.

Suppose the user asks:
What is the refund period for the product
that replaced the old Enterprise plan?

You cannot directly search:
refund period for ???

because you don't yet know the product.

So:
Original question
       ↓
Hop 1:
What product replaced the old Enterprise plan?
       ↓
Retrieved evidence:
"Enterprise Plus replaced Enterprise."
       ↓
Extract:
Enterprise Plus
       ↓
Hop 2:
What is the refund period for Enterprise Plus?
       ↓
Retrieved evidence:
"Enterprise Plus has a 45-day refund period."
       ↓
Final answer

The word hop just means one retrieval/reasoning step.

### Why ordinary RAG fails here
Normal RAG does:
question
   ↓
one retrieval
   ↓
documents
   ↓
LLM

But the original question contains an indirect reference:
"the product that replaced..."

Your refund document might never mention:
old Enterprise plan

And the replacement-announcement document might never mention:
refund period

So no single chunk has enough information.

You need to connect:
Enterprise
   ↓ replaced by
Enterprise Plus
   ↓ has policy
45 days

That's the purpose of multi-hop retrieval.

### What actually runs the hops?
Your application needs an orchestration layer.

Conceptually it maintains some state:
state = {    "original_question": "...",    "known_facts": [],    "retrieved_documents": [],    "next_query": None}


state isn't special RAG magic. It's just data your program keeps while solving the question.

After hop 1:
state["known_facts"] = [    "Enterprise Plus replaced Enterprise."]


Then your code or an LLM generates the next query:
state["next_query"] = (    "What is the refund policy for Enterprise Plus?")


Then retrieve again.

This is one reason something like LangGraph becomes useful: it can represent:
retrieve
   ↓
inspect result
   ↓
decide what to search next
   ↓
retrieve again

But LangGraph is not required. Plain Python can absolutely implement this.

### Who decides the next query?
There are two broad possibilities.

If the process is predictable, your code can determine it.

For example:
replacement = extract_product_name(result)next_query = f"What is the refund policy for {replacement}?"


For flexible questions, an LLM is often used.

You might give it:
Original question:
What refund policy applies to the product that replaced Enterprise?

Evidence discovered:
Enterprise Plus replaced Enterprise.

What information is still missing?

It might produce:
We still need the Enterprise Plus refund policy.

Next search:
Enterprise Plus refund policy

So yes, a flexible multi-hop system can involve several LLM calls.

Potentially:
LLM → decide first search
retrieval
LLM → inspect evidence / create next search
retrieval
LLM → final answer

This can get expensive, which is why you don't make every query multi-hop.

### How does the system know when to stop?
Very important.

Without a stopping rule you could create:
search
→ think
→ search
→ think
→ search
→ ...

forever.

A system usually stops when it believes it has enough evidence to answer.

Conceptually:
Do I have sufficient evidence?
        │
     yes│no
        │
   answer  generate next query

You can also enforce hard limits:
maximum_hops = 3

or:
maximum_retrieval_calls = 5

That protects latency and cost.

A good system usually has both:
semantic stopping condition
+
hard safety limit

### Multi-hop does not necessarily mean an agent
This is another distinction worth getting right.

You can build a fixed workflow:
retrieve entity
↓
retrieve property of entity
↓
answer

That's multi-hop but not necessarily agentic.

An agentic version has more freedom:
Should I search?
What should I search?
Which source?
Should I search again?
Should I use another tool?
Do I have enough evidence?

So:
multi-hop retrieval
⊂ possible agentic behavior

but multi-hop itself does not require an agent.


# Routing
           User query
              ↓
            Router
         /     |      \
        /      |       \
    policies   DB    engineering
        ↓      ↓         ↓
    retrieve/query appropriate source