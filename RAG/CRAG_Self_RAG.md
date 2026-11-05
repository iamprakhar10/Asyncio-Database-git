# Corrective RAG
CRAG is an advance RAG design pattern that introduces a self-evaluation and self-correction layer between the retrieval phase and generation phase

##### Why is it needed? - Blind trust problem in standard RAG
Standard RAG pipeline works on the assumption that whatever gets retrieved from vector search is relevant

1. In real world that assumption breaks constantly
Semantic Mismatch: A user query might use terminology slightly differently than your documentation, causing the vector database to pull completely irrelevant or tangential chunks.

2. Missing Knowledge: If the exact answer doesn't exist in your internal database, a standard RAG system will still retrieve the "closest possible" documents (which are actually useless) and force the LLM to hallucinate an answer out of garbage context.

3. Noisy/Contradictory Context: Pulling 5 chunks where 2 are relevant and 3 are misleading often confuses the LLM, leading to inaccurate outputs.

##### CRAG workflow
CRAG solves the *Garbage in, Garbage out* bottleneck of context assembly by routing retrieved documents through a strict evaluation gate

When a query runs through a CRAG architecture, it follows these precise steps:
###### Initial Retrieval: 
The system pulls candidate chunks from your knowledge base (using vector search or hybrid BM25).

###### Evaluation (The Grader): 
A fast evaluator (either a lightweight fine-tuned classifier or a structured LLM call) assesses the relevance of each retrieved document against the user query. It assigns confidence scores, sorting them into three distinct paths:   

1. Correct: At least one document is highly relevant. The system triggers knowledge refinement (stripping out noisy sentences and keeping only the precise data strips).   
2. Incorrect: All retrieved documents fail the relevance threshold. The system discards them entirely, preventing hallucinations, and dynamically triggers an external fallback (such as a live web search via APIs like Tavily) to fetch fresh data.   
3. Ambiguous: The results are mixed or unclear. The system combines the partially useful internal chunks with external web search augmentation to bridge the gaps.   

###### Generation: 
The LLM receives only pre-vetted, high-confidence, corrected context.  


##### Is It Just Theory or Used in Industry?
It is heavily used in production engineering, particularly in high-stakes enterprise applications.
While basic tutorials love to showcase simple 50-line RAG scripts, enterprise platforms cannot afford hallucinations when dealing with legal compliance, financial auditing, technical customer support, or medical guidelines.


##### How It Shows Up in Modern Tech Stacks:
1. Orchestration Frameworks: Frameworks like LangGraph and LlamaIndex feature native templates and state-graph primitives specifically designed to build CRAG loops (conditional routing edges based on evaluator node outputs).   
2. Enterprise Search & Agentic Systems: Production teams implement "evaluator-optimizer" loops where an agent checks its retrieved context before writing a response. If confidence scores drop below a threshold, the system automatically rewrites the query or fetches external data instead of failing silently.

The trade-off is latency and cost—adding evaluation steps and potential web search fallbacks adds extra milliseconds and token overhead to every request. However, for production systems where accuracy is non-negotiable, that overhead is a mandatory price of admission.