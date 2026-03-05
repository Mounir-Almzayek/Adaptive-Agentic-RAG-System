# Glossary — Adaptive Agentic RAG System

| Term | Definition |
|------|------------|
| **Adaptive RAG** | Retrieval strategy that chooses or falls back (e.g. vector → hybrid) based on result quality or count. |
| **Agent** | LangChain-based agent (e.g. ReAct) that uses an LLM and tools to answer queries; may use retrieved docs as context. |
| **CRAG** | Corrective RAG: validate the model answer and, on failure, re-retrieve (e.g. higher top_k or hybrid) and re-generate. |
| **Hybrid search** | Retrieval combining vector similarity and keyword/BM25 (or similar) for better recall. |
| **Ingestion** | Loading documents (PDF, text, etc.), chunking, and indexing into the vector store. |
| **LangChain** | Framework for chains, agents, tools, vectorstores, and LLM abstractions. |
| **LCEL** | LangChain Expression Language; composable runnables. |
| **MCP** | Model Context Protocol; in this project, “MCP-ready” means exposing RAG as HTTP tools for external agents. |
| **Model factory** | Factory that creates a LangChain LLM instance from config (provider, model id, API key). |
| **OpenRouter** | API gateway that routes to multiple LLM providers (OpenAI, Google, Anthropic, etc.) with one API key. |
| **RAG** | Retrieval-Augmented Generation: retrieve relevant docs, then generate an answer using them as context. |
| **RAGService** | Single entry-point service that coordinates retrieval, memory, and agent for a user query. |
| **Reranker** | Optional step that reorders retrieved chunks by relevance (e.g. cross-encoder). |
| **Retrieval engine** | Component that runs `retrieve(query, strategy)` and returns a list of documents (vector/hybrid/adaptive). |
| **Tool registry** | Central place to register and retrieve tools used by the agent (e.g. search_knowledge, calculator). |
| **Vector store** | Storage and search over embeddings (e.g. Chroma, FAISS) for semantic retrieval. |
