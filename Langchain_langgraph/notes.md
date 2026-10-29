# Langchin
Langchain is basically an application framework used for making AI powered systems. It makes orchestration between different components easy.

It gies us reusable abstractions for things we repeatedly need when building AI apps: calling models, formatting prompts/messages, invoking tools, connecting retrievers/vector stores, handling structured outputs, and composing these pieces into agents or workflows.

It's current ecosystem also includes LangGraph for more controlled, stateful agents and langsmith for evaluation/observability

Imagine you want to build this:

User → AI → search company docs → call database → maybe use calculator → decide next action → respond

Without a framework, you write all the plumbing yourself:
call model
parse response
detect tool call
execute tool
send result back
call model again
maintain conversation state
handle retry
handle failure
log everything
repeat...


Instead of tightly coupling your code to one model provider, LangChain gives you a fairly consistent interface across providers. It similarly provides integrations for embeddings, vector databases, retrievers, tools, and other components, which makes experimentation easie

For structured output, sometimes LangChain adds formatting instructions to the prompt, but not always. In modern models, the better path is often to use the model provider’s native structured-output or tool-calling API instead of relying only on prompt text.

Model outputs should match the JSON schema supplied by us.
Structured uotput can be understood as difference between suggesting to the model vs constraining it.
It's not just about asking nicely 

They used constrained decoding, let's talk about 
- LLM inference
- Token Masking - Constrains which tokens can be picked at the very end of samppling. When sampling JSON for our schemas , we need to update the masked tokensat every step of inference.
- Subset of JSON schemas

| Step | Input                         | Mask                   | Sampled |
|------|-------------------------------|------------------------|---------|
| 0    | `USER_INPUT`                  | `{`, `\n`, `\n\t`      | `{`     |
| 1    | `USER_INPUT + {`              | `\n`, `\n\t`, `"`, `"val` | `\n\t` |
| 2    | `USER_INPUT + { + \n\t`       | `\t`, `"`, `"val`, `"v`  | `"val` |
| 3    | `USER_INPUT + { + \n\t + "val` | `u`, `ue`             | `ue`      |



| GPU time                              | CPU time                     |
|---------------------------------------|------------------------------|
| Calculate probabilities for batch 1   |                              |
|                                       | Calculate mask for batch 2   |
| Calculate probabilities for batch 2   |                              |
|                                       | Calculate mask for batch 3   |
| Calculate probabilities for batch 3   |                              |


We need the mask to happen in about same amount of time as calculating probabilities(Time betwen tokens)

A naive solution to this problem would involve determining these valid tokens from the current state at every step of inference.

So we want to precompute as much work as possible and then reuse it when sampling to make mass computation more like a lookup and less like a lot of work.

Just like we can build index in our database to speed up our queries, we can build up our index with specific JSON schema that we supply to make fetching these masks very fast during inference

Lot of work that goes into producing this index from JSON schema


1. First we convert JSON schema into a grammar(formal specification of a language)

2. Once we have a grammar, we can create a parser(a program that can check strings and see if they're part of this language). Think parser as a program that takes in a JSON blob and tells us does this match the schema or not

3. Once we have the parser, we can iterate over all of the tokens in our vocabulary and all of the states that are possible in the parser, and this will determine which tokens are valid

4. This work lets us build an index. Our index is actually a tree(preficx based data structure that allows O(1) lookups).



During inference we are running our parser, building up some states and every time we'll traverse this tree ti find the leaf. The leaf node will tell us what the mask is for the next step

Generating these indexes is computationally exppensive(we have to go over all of the possible states). So we just do it once and then cache it later for faster lookups

Tradeoff: Waiting a little longer for our first request whilewe are developing
The following queries are fast

##### Supported grammars with structured outputs
Regular expressions(regex) work for simple, depth-limited schemas

However we can't cover all of the expressiveness with JSON schemas with reular expressions. They are missing basically the memory needed to storeinformations about past lookups which is important

CFG(context free grammar) = regular expression + stack

It took time for OpenAI to build up this tree for inference(also supports recursio in deep nesting)

And due to these works it gets the job done 100% of time(format of the output)

#### output parser
Prompt: "Return JSON"
        ↓
LLM
        ↓
Maybe valid JSON
Maybe malformed JSON
Maybe extra explanation
        ↓
Output Parser
        ↓
Clean/parse/validate it


OLD:
Generate anything → parse/fix afterward

NOW:
Specify schema → constrain generation → validate result

So parsers were needed to:
- extract JSON from text
- remove extra prose
- convert strings into Python objects
- validate fields
- sometimes retry when formatting was wrong
Output parsers still matter for older/local models, custom text formats, streaming, and cleanup—but for normal JSON structured output, they are no longer the primary solution.


#### Chains
Output of one component becomes the Input of the other 
Sequential  = A → B → C
Runs components one after another. Output of one becomes input to the next.


Parallel    = A → [B, C, D]
Sends the same/input-derived data to multiple components concurrently, then combines their outputs. 
Eg-> Run sentiment analysis, summarization, and classification at the same time.
               ┌──→ Step A ──┐
Input ─────────┼──→ Step B ──┼──→ Combined Result
               └──→ Step C ──┘

chain = RunnableParallel(
    summary=summary_chain,
    sentiment=sentiment_chain,
)

Conditional = A → B OR C OR D
Chooses which branch to execute based on a condition or routing decision
Eg-> execute based on a condition or routing decision.	Route a query to coding, research, or support pipeline.

In LangChain this can be implemented with runnable branching/routing; for larger, stateful branching workflows, LangGraph is usually the better abstraction.

#### Runnables
Langchain dfines runnables as a "unit of work" that can be invoked, streamed, batched, transformed, and composed.

Many things can behave like runnables:
Prompt
Model
Retriever
Parser
Custom Python function
Entire chain

So instead of every component having a completely different way of being executed, they can all behave roughly like:

component.invoke(input)

A Runnable gives every LangChain component a common Input → Output interface so components can be composed, streamed, batched, run asynchronously, retried, and reused consistently

await chain.ainvoke(...)
means:
run it asynchronously so other async work can proceed while this is waiting

TASK-SPECIFIC RUNNABLES
= "What work should happen?"

LLM
Retriever
Prompt
Parser


RUNNABLE PRIMITIVES
= "How should that work be connected?"

1. RunnableSequence
A → B → C

2. RunnableParallel
       ┌→ B
A ─────┼→ C
       └→ D

Runs multiple Runnables concurrently and combines their results. RunnableSequence and RunnableParallel are currently LangChain's two main composition primitives.


3. RunnableLambda

Turns your normal Python function into a Runnable:
def clean(x):
    return x.strip()

clean_runnable = RunnableLambda(clean)

Now it can participate in a chain: prompt | model | clean_runnable

4. RunnablePassthrough

Passes input through unchanged, useful when you need to preserve data while computing something else.

For example in RAG

Task-specific Runnables do the work. Runnable primitives orchestrate the work.












# LangGraph 
LangGraph is not industry standard, there is currently no universal standard for agent orchestration yet

It's job is to control what happens around the LLM: state, branching, loops, retries, persistence, human approval, resumability, streaming, and long-running execution.

Even a simple chain is manageable:
User
 ↓
Retriever
 ↓
LLM
 ↓
Parser

But real agents start looking like:
                    ┌──── Search Web ────┐
                    │                    │
User → Understand → Decide → Call DB ────┤
                    │                    │
                    ├──── Ask Human ─────┤
                    │                    │
                    └──── Retry Tool ────┘
                              │
                              ↓
                           Continue
                              │
                              ↓
                            Finish

Now you need to answer:
- What state does the agent currently have?
- Which node runs next?
- What if a tool fails?
- What if the process crashes halfway through?
- How do I resume?
- How do I pause for human approval?
- How do I avoid repeating a payment/refund/tool call?
- How do I loop back to an earlier step?
- How do I preserve conversation/task state?
You can write all of this yourself, but it quickly becomes complicated.

That is the problem LangGraph tries to solve.

LangGraph = State + Nodes + Edges

A Node perform some work. A node can just be normal Python code, an LLM call, a tool call, or even another graph.

Edges determine what happens next

State is the information moving through the graph.

state = {
    "messages": [...],
    "user_id": "...",
    "documents": [...],
    "tool_results": [...],
    "status": "waiting_for_approval"
}

Every node reads some state and updates it.

agents often need:
          ┌──────────────┐
          ↓              │
A → B → Decision → C → Check
        │                 │
        └→ Human          │
             ↓            │
           Resume ────────┘

Now you have:

loops + persistent state + branching + interruptions + resumability.

That's where a graph/state-machine abstraction becomes much cleaner.

#### One of its biggest features: durable execution

Imagine:
Step 1: Retrieve customer
Step 2: Analyze refund
Step 3: Human approves
Step 4: Issue refund
Step 5: Email customer

At Step 3 the process may pause for two hours waiting for a human.

You don't want a Python function sitting there:
wait_for_two_hours()


Instead LangGraph can persist/checkpoint the state:
Customer found ✓
Analysis done ✓

──── SAVED STATE ────

Waiting for human...

        ↓ later

Resume

        ↓

Issue refund
        ↓
Send email

LangGraph explicitly provides persistence, durable execution and human-in-the-loop functionality for this kind of workflow. GitHub

**** This is a much bigger reason to use LangGraph than just drawing pretty graphs. ****

#### Another big feature: human-in-the-loop
Suppose an agent wants to transfer ₹100,000.

You probably don't want:
LLM decides
   ↓
transfer_money()

You want:
LLM proposes transfer
        ↓
┌─────────────────────┐
│ HUMAN APPROVAL      │
└──────────┬──────────┘
           │
      ┌────┴────┐
      ↓         ↓
   Approve    Reject
      ↓
 Execute

LangGraph supports pausing and resuming workflows around these intervention points.


#### You can even build the graph yourself
For example:
state = {}
current_node = "reason"
while current_node != "END":
    if current_node == "reason":
        state = reason(state)
        current_node = choose_next(state)    
    elif current_node == "search":
        state = search(state)        
        current_node = "reason"    
    elif current_node == "human":
        save_state(state)        
        break


That is essentially the kind of orchestration problem LangGraph helps formalize.

As your application gets more complicated, you eventually start implementing:
state persistence
checkpointing
branching
interrupts
resume
streaming
retries
subgraphs
parallel execution
error handling

Then you may realize:
"I'm slowly rebuilding LangGraph."

That's usually the point where a framework becomes useful.

LangGraph is used because it eases us from the work of writing glue code of cranch, loop, retries etc

Langchain doesn't provide sunctionality of pause, fault tolerance/error handling

LangGraph allows Nested workflows, also used for milti agent  

1. State = the shared data for the workflow right now, like messages, tool results, counters, status.

2. Node = a unit of work that reads state and returns updates, e.g. “call LLM” or “search DB.”

3. Edge = decides which node runs next; can be fixed or conditional.

4. Reducer = defines how a node’s update is merged into existing state.
Without a reducer, an update might simply overwrite the old value.
___________________
#### LangGraph Execution model
LangGraph uses a Pregel-inspired, bulk-synchronous execution model. The important idea is that the graph executes in discrete rounds called supersteps, rather than recursively calling nodes however they want. LangChain

Suppose you define:
          ┌──> B ──┐
START → A ┤        ├→ D → END
          └──> C ──┘

Execution is roughly:
Initial State
     │
     ▼
────────────────────
SUPERSTEP 1
────────────────────
     Node A
       │
       │ returns state update
       ▼
   apply reducer(s)

────────────────────
SUPERSTEP 2
────────────────────
   Node B      Node C
      │          │
      └────┬─────┘
           │
     both return updates
           │
           ▼
      reducers merge them

────────────────────
SUPERSTEP 3
────────────────────
          Node D
            │
            ▼
           END

Nodes scheduled in the same superstep can execute concurrently. Their state writes are collected and committed at the superstep boundary, so one parallel node does not simply see another parallel node's partially completed update


Parallel nodes can READ the whole state.        
✓

Parallel nodes should RETURN only their updates, not the whole state. ✓

Parallel nodes writing the same key
without a reducer                              
✗

#### LangGraph parallelism
LangGraph parallelism is not claiming some magical new kind of parallelism.

LangGraph provides the orchestration semantics:
Which nodes are runnable?
Which ones can run together?
When do we wait?
When do we merge state?
What happens if one fails?
What runs next?

The underlying concurrency is still implemented using ordinary programming/runtime mechanisms like futures, executors, threads, or async tasks.

So:
LangGraph decides what can run concurrently; Python/runtime mechanisms decide how that concurrency is executed.

And if your nodes are CPU-heavy Python calculations, threads may not speed them up much because of the GIL. Then you’d want processes, native code, GPUs, or distributed workers instead.


#### Conditional edges

1. With an explicit mapping
graph.add_conditional_edges(
        "evaluate",
        route_evaluation,
        {        
                "approved": END,
                "needs_improvement": "optimize"    
        }
)


Here route_evaluation(state) returns a logical label:
def route_evaluation(state):
    if state["score"] > 0.8:
        return "approved"
    return "needs_improvement"


LangGraph then translates that label using the mapping:
"approved"           → END
"needs_improvement"  → "optimize"

So the router function does not need to know actual graph node names.
2. Without a mapping

graph.add_conditional_edges(
    "calculate_discriminant",
    check_condition
)


Now check_condition(state) must usually return the actual destination node name directly:
def check_condition(state):
    if state["discriminant"] > 0:
        return "two_roots"
    elif state["discriminant"] == 0:
        return "one_root"    
    else:
        return "no_real_roots"


So:
check_condition()
       ↓
returns "two_roots"
       ↓
LangGraph goes directly to node "two_roots"

The mapping version is often cleaner because your routing logic can return semantic decisions like "approved" instead of being tightly coupled to graph node names
#### Iterative workflow


#### RAG Safety
. RAG (Retrieval-Augmented Generation) can be engineered to be completely secure and private.

The misconception that RAG inherently compromises data safety usually comes from looking at the "naive tutorial" version of RAG—where someone drops every internal document into a public cloud vector store and sends it to a public API.

When built with proper enterprise boundaries, RAG is one of the safest ways to give an LLM private context without exposing your core database. Here is how a fully secure, airtight RAG architecture is built:

1. Host Your Own Vector Database
In RAG, your documents don't go to the LLM provider for training; they live in a vector database (like Qdrant, Milvus, or pgvector inside your own PostgreSQL database).If you host your vector database within your own secure VPC or on-premise server, your raw documents and embeddings never leave your infrastructure.

2. Enforce Access Control at Retrieval Time
To prevent unauthorized data leaks, you don't let the vector search pull everything blindly. You attach metadata tags to your document chunks (e.g., department: HR, clearance_level: confidential).

When a user queries the system, your vector search query includes strict metadata filters: WHERE department = 'Engineering' AND user_clearance >= chunk.clearance.

The system physically cannot retrieve a document the user isn't allowed to see.

3. Pair It with Local InferenceIf you pair your private, access-controlled vector database with a self-hosted LLM running locally via vLLM, your entire data loop—from document parsing to embedding to final text generation—happens entirely on hardware you own and control. Zero bytes touch the public internet.

RAG is just a design pattern: 
Search documents --> Inject into prompt --> Generate answer. Because you build and configure every piece of that pipeline, its security is entirely up to your architecture.

###### adding reducers
import operator

->state
class TweetState(TypedDict):
        tweet_history: Annotated[list[str], operator.add]
        feedback_history: Annotated[list[str], operator.add]


Now any change in tweet history will not replace the old value, it will append the new value

#### Persistence
Persistence in LnagGraph refers to the ability to save and restore the state of a workflow over time

Checkpointers in persistance
checkpointer is the persistence layer that automatically saves the exact state of your graph after every single execution step (called a "super-step")

Without a checkpointer, a langGraph aplication is stateless, once a request finishes or server restarts, all memory of what happened is lost.
 Checkpointers ebnable 4 critical production features

1. Persistance and fault tolerance (we applied without LangGraph in ABTO)
2. HITL - Checkpointers make it trivial to pause a graph right before a sensitive action, wait foro human to approve, and then resume the graph from that exact saved state
3. Time travel and Debugging - Because every step is saed with a unique identifier, we can "rewind" our graph to an earlier state, inspect what went wrong, or even fork execution down a braind-new path from a past checkpoint
4. Multi-Turn Conversational Threads - By passing a thread_id in runtime cofiguration, the graph pulls the previous state associated with that thread, giving our agent persistent memory across multiple user interactions

##### Persistence under the hood
When we invoke a graph with checkpointer attached, ttwo things happen:

1. State serialization: LangGraph takes current state(defined by TypedDict or Pydantic model) and serializes it.
2. Key value Storage: It writes that state to storage backend using a composite key consisting of a thread_id and a monotonic checkpoint id

LangGraph provides different checkpointer implementations depending on your infrastructure needs:

MemorySaver: Stores states in local RAM. Perfect for local development, testing, and scripts, but data is lost when the Python process restarts.

SqliteSaver / PostgresSaver: Persists states to a relational database. This is what you use in production multi-container architectures to ensure state survives server reboots and scales across multiple app instances.