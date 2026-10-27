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

Model outputs should match the JSON schema supplied by us