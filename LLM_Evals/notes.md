LLM Evals:
LLM evals are systematic, repeatable tests used to judge an LLM or LLM-powered system against a clear criteria
Repeatable-> If we change the prompt, model, retriever, chunking stratergy, or system instruction, we should be able to run the same test again and compare the result

Clear criteria->
For example a good answer should be
-correct
- simple explanation
- safe policy complaint

An eval is not just a metric. It's a complete testing setup, in includes
- What are we testing
- what does good mean
- What test cases are we using
- How are we judging the output
- when are we runnign it
- Which tool are we using

The goal is not just to get a score. The goal is to answer practical questions like:
- Can the model be used for a particular task/application?
- Did prompt v2 improve over prompt v1?
- Is the RAG answer grounded in the retrieved context?
- Is the latency under control?


Model capabulities are generally evaluated using *benchmarks*. 

How to evaluate any application using LLM(not the LLM itself)
One LLM based application might have several evals 

Why our AI application needs multiple Evals

### LLM Application Evals - Methods
Mechanism we use to decide whether an LLM's output is good or not - the actual procedure that takes in input an produces a judgement about it

- Deterministic
- Human
- Model-graded(LLM as Judge)

                    Deterministic     Non-deterministic
Reference-based     Exact match       LLM judge vs gold answer
Reference-free      Rule/state checks LLM judge on quality

Reference-based vs reference-free = what you evaluate against.
Deterministic vs non-deterministic = whether the evaluator always produces the same result for the same input.

A rubric is just a clear scoring rule that tells the evaluator exactly what each score means
A rubric makes the standard explicit:
5 = fully correct, relevant, clear, and complete
4 = mostly correct, with a minor omission
3 = partially correct, but misses an important point
2 = major mistakes or poor relevance
1 = mostly incorrect or unusable

### Offline vs Online evals
evals before deploying is ofline Eval
why do we need it?
- Pre-release tseting
- Version comparision
- Regression Testing

###### What about post deployment?
1. Unanticipated inputs -> (hindi english mix question, half questions, angry rants,adverserial prompt-injection attempts, or in short the edge-cases we never considered)
2. Emergent/systematic failure -> Problems that only exist at scale, under laod, over time
3. Drift -> When offline eval goes obsolete

Online evals is evaluating our system on live production traffic,after deployment, as real users interact with it
Biggest challange => No golden dataset here


# LLM Model evals and their capabilities
Why?
- To comparedifferent models fairly
- To track whether newer models are improving
- Is the model safe

### Custom model evals for our required job

