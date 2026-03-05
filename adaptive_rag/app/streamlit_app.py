"""
Streamlit UI for the Adaptive Agentic RAG System.

Thin view layer: chat display, file upload for ingestion, and settings in the sidebar.
All logic is delegated to RAGService and IngestionService (built via app_factory).
"""

from __future__ import annotations

import streamlit as st

# Session state keys
KEY_MESSAGES = "messages"
KEY_RAG_SERVICE = "rag_service"
KEY_INGESTION_SERVICE = "ingestion_service"
KEY_RETRIEVAL_STRATEGY = "retrieval_strategy"
KEY_SELF_CHECK = "enable_self_check"

# Supported file extensions for upload (must match IngestionService)
UPLOAD_EXTENSIONS = {".pdf", ".txt", ".md"}


def _ensure_services():
    """Build and cache RAGService and IngestionService in session state. Returns (rag_service, ingestion_service) or (None, None) on error."""
    if KEY_RAG_SERVICE in st.session_state and KEY_INGESTION_SERVICE in st.session_state:
        return st.session_state[KEY_RAG_SERVICE], st.session_state[KEY_INGESTION_SERVICE]
    try:
        from adaptive_rag.services.app_factory import build_rag_service_with_ingestion

        enable_self_check = st.session_state.get(KEY_SELF_CHECK, False)
        rag_service, ingestion_service = build_rag_service_with_ingestion(
            enable_self_check=enable_self_check,
            default_top_k=5,
        )
        st.session_state[KEY_RAG_SERVICE] = rag_service
        st.session_state[KEY_INGESTION_SERVICE] = ingestion_service
        return rag_service, ingestion_service
    except Exception as e:
        st.error(f"Failed to load RAG: {e}. Check OPENROUTER_API_KEY in .env.")
        return None, None


def _render_sidebar():
    st.sidebar.title("Adaptive RAG")
    st.sidebar.caption("Model-agnostic • Multi-provider • MCP-ready")

    # Retrieval strategy (passed to ask() each time; no rebuild)
    strategy = st.sidebar.selectbox(
        "Retrieval strategy",
        options=["adaptive", "vector", "hybrid"],
        index=0,
        help="Adaptive: vector first, fallback to hybrid if few results.",
    )
    st.session_state[KEY_RETRIEVAL_STRATEGY] = strategy

    st.sidebar.checkbox(
        "Enable self-check (CRAG)",
        key=KEY_SELF_CHECK,
        value=False,
        help="Validate answer and retry with broader retrieval once if needed.",
    )

    st.sidebar.divider()
    st.sidebar.subheader("Knowledge base")

    # File upload: only process when we have ingestion service (after first load or after first message)
    uploaded = st.sidebar.file_uploader(
        "Upload document (PDF, TXT, MD)",
        type=[e.lstrip(".") for e in UPLOAD_EXTENSIONS],
        help="Files are chunked and indexed for retrieval.",
    )
    if uploaded:
        name = uploaded.name
        suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if suffix not in UPLOAD_EXTENSIONS:
            st.sidebar.warning(f"Unsupported type {suffix}. Use PDF, TXT, or MD.")
        else:
            rag, ing = _ensure_services()
            if ing is not None:
                try:
                    import tempfile
                    from pathlib import Path

                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                        f.write(uploaded.getvalue())
                        path = f.name
                    n = ing.ingest_file(path)
                    Path(path).unlink(missing_ok=True)
                    st.sidebar.success(f"Ingested {n} chunk(s) from {name}.")
                except Exception as e:
                    st.sidebar.error(f"Ingestion failed: {e}")
            else:
                st.sidebar.info("Send a message first to initialize RAG, then upload.")

    if st.sidebar.button("Clear conversation memory"):
        if KEY_RAG_SERVICE in st.session_state:
            st.session_state[KEY_RAG_SERVICE].clear_memory()
        if KEY_MESSAGES in st.session_state:
            st.session_state[KEY_MESSAGES] = []
        st.sidebar.success("Memory cleared.")
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Config from .env (OPENROUTER_API_KEY, DEFAULT_MODEL, etc.).")


def main():
    st.set_page_config(
        page_title="Adaptive Agentic RAG",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if KEY_MESSAGES not in st.session_state:
        st.session_state[KEY_MESSAGES] = []

    _render_sidebar()

    # Main chat area
    st.title("Adaptive Agentic RAG")
    st.caption("Ask questions. Upload documents in the sidebar to search over your knowledge base.")

    for msg in st.session_state[KEY_MESSAGES]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Your question"):
        st.session_state[KEY_MESSAGES].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            rag_service, _ = _ensure_services()
            if rag_service is None:
                response_text = "RAG is not loaded. Set OPENROUTER_API_KEY in .env and reload."
            else:
                strategy = st.session_state.get(KEY_RETRIEVAL_STRATEGY, "adaptive")
                try:
                    response = rag_service.ask(prompt, strategy=strategy)
                    response_text = response.content
                    if response.used_corrective_retry:
                        st.caption("_(Corrective retrieval was applied.)_")
                except Exception as e:
                    response_text = f"Error: {e}"

            st.markdown(response_text)

        st.session_state[KEY_MESSAGES].append({"role": "assistant", "content": response_text})
        st.rerun()


if __name__ == "__main__":
    main()
